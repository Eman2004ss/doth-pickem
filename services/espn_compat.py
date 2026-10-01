"""Robust ESPN schedule lookup used by the admin and live score updater.

The original project searched only ESPN's default *current* scoreboard, which
means future Week 1 games often reported "No ESPN match" even when ESPN had
an event.  This module searches the season schedule by season type/week and
uses ESPN's event-summary endpoint for already-linked games.
"""

from datetime import datetime, timezone
import re
import time
import unicodedata

import requests

import services.espn_service as legacy


_CACHE = {}
_CACHE_SECONDS = 300
_SESSION = requests.Session()


def _sport_path(sport):
    selected = (sport or "ncaa").lower()
    if selected == "nfl":
        return "football", "nfl"
    if selected == "nhl":
        return "hockey", "nhl"
    return "football", "college-football"


def _scoreboard_url(sport):
    category, league = _sport_path(sport)
    return (
        "https://site.api.espn.com/apis/site/v2/sports/"
        f"{category}/{league}/scoreboard"
    )


def _summary_url(sport):
    category, league = _sport_path(sport)
    return (
        "https://site.api.espn.com/apis/site/v2/sports/"
        f"{category}/{league}/summary"
    )


def _teams_url(sport):
    category, league = _sport_path(sport)
    return (
        "https://site.api.espn.com/apis/site/v2/sports/"
        f"{category}/{league}/teams"
    )


def _team_schedule_url(sport, team_id):
    category, league = _sport_path(sport)
    return (
        "https://site.api.espn.com/apis/site/v2/sports/"
        f"{category}/{league}/teams/{team_id}/schedule"
    )


def _normalize(value):
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _team_names(team):
    candidates = {
        team.get("displayName"),
        team.get("shortDisplayName"),
        team.get("name"),
        team.get("location"),
        team.get("abbreviation"),
    }
    return {_normalize(name) for name in candidates if name}


def _team_matches(target, team):
    target = _normalize(target)
    if not target:
        return False
    names = _team_names(team)
    if target in names:
        return True
    # Also accept a full-name target when ESPN omits punctuation or a short
    # qualifier.  Require token containment in both directions to avoid loose
    # one-word matches such as "Tigers".
    target_tokens = set(target.split())
    if len(target_tokens) < 2:
        return False
    for name in names:
        name_tokens = set(name.split())
        if len(name_tokens) >= 2 and (
            target_tokens.issubset(name_tokens) or name_tokens.issubset(target_tokens)
        ):
            return True
    return False


def _cached_scoreboard(sport, season, season_type, week):
    key = ((sport or "ncaa").lower(), int(season), int(season_type), int(week))
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < _CACHE_SECONDS:
        return cached[1]

    params = {
        "dates": str(season),
        "seasontype": int(season_type),
        "week": int(week),
        "limit": 1000,
    }
    try:
        response = _SESSION.get(_scoreboard_url(sport), params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        payload = None
    _CACHE[key] = (now, payload)
    return payload


def _event_competitors(event):
    competitions = event.get("competitions") or []
    if not competitions:
        return None, None
    competitors = competitions[0].get("competitors") or []
    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
    return away, home


def _team_data(competitor):
    if not competitor:
        return {}
    team = competitor.get("team") or {}
    records = competitor.get("records") or []
    logos = team.get("logos") or []
    return {
        "team_name": team.get("displayName") or team.get("shortDisplayName") or "",
        "espn_team_id": team.get("id"),
        "abbreviation": team.get("abbreviation"),
        "record": records[0].get("summary", "") if records else "",
        "logo": logos[0].get("href") if logos else None,
    }


def _event_result(event, sport):
    away, home = _event_competitors(event)
    if not away or not home:
        return None
    status_type = (event.get("status") or {}).get("type") or {}
    return {
        "event_id": event.get("id"),
        "kickoff": event.get("date"),
        "away_team": _team_data(away),
        "home_team": _team_data(home),
        "sport": (sport or "ncaa").lower(),
        "status": status_type.get("description", "Scheduled"),
    }


def _event_orientation(event, away_name, home_name):
    """Return normal/reversed when the two selected teams match an ESPN event."""
    away, home = _event_competitors(event)
    if not away or not home:
        return None

    away_team = away.get("team") or {}
    home_team = home.get("team") or {}

    if _team_matches(away_name, away_team) and _team_matches(home_name, home_team):
        return "normal"

    if _team_matches(away_name, home_team) and _team_matches(home_name, away_team):
        return "reversed"

    return None


def _matched_result(event, away_name, home_name, sport):
    orientation = _event_orientation(event, away_name, home_name)
    if not orientation:
        return None

    result = _event_result(event, sport)
    if result:
        result["orientation"] = orientation
    return result


def _search_plan(sport):
    if (sport or "ncaa").lower() == "nfl":
        # preseason, regular season, postseason
        return [(1, range(1, 6)), (2, range(1, 19)), (3, range(1, 7))]
    # College schedules occasionally expose Week 0 and can extend through
    # conference championships/postseason.
    return [(2, range(0, 17)), (3, range(1, 8))]


def _cached_nhl_scoreboard(start_day, end_day=None):
    end_day = end_day or start_day
    date_key = (
        start_day.strftime("%Y%m%d")
        if start_day == end_day
        else f"{start_day.strftime('%Y%m%d')}-{end_day.strftime('%Y%m%d')}"
    )
    key = ("nhl-date", date_key)
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < _CACHE_SECONDS:
        return cached[1]

    try:
        response = _SESSION.get(
            _scoreboard_url("nhl"),
            params={"dates": date_key, "limit": 1000},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        payload = None

    _CACHE[key] = (now, payload)
    return payload


def _cached_nhl_teams():
    key = ("nhl-teams",)
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < _CACHE_SECONDS:
        return cached[1]

    try:
        response = _SESSION.get(
            _teams_url("nhl"),
            params={"limit": 100},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        payload = None

    _CACHE[key] = (now, payload)
    return payload


def _iter_team_objects(payload):
    """Yield ESPN team dictionaries from the /teams response."""
    sports = (payload or {}).get("sports") or []
    for sport in sports:
        for league in sport.get("leagues") or []:
            for item in league.get("teams") or []:
                team = item.get("team") or item
                if isinstance(team, dict):
                    yield team


def _find_nhl_team_id(team_name):
    payload = _cached_nhl_teams()
    for team in _iter_team_objects(payload):
        if _team_matches(team_name, team):
            team_id = team.get("id")
            if team_id is not None:
                return str(team_id)
    return None


def _cached_nhl_team_schedule(team_id, season):
    key = ("nhl-team-schedule", str(team_id), int(season))
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < _CACHE_SECONDS:
        return cached[1]

    try:
        response = _SESSION.get(
            _team_schedule_url("nhl", team_id),
            params={"season": int(season)},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        payload = None

    _CACHE[key] = (now, payload)
    return payload


def _parse_event_time(event):
    raw = event.get("date")
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _find_nhl_event_from_team_schedule(away_team_name, home_team_name):
    """Choose the nearest future matching NHL event from full team schedules."""
    candidate_ids = []
    for team_name in (away_team_name, home_team_name):
        team_id = _find_nhl_team_id(team_name)
        if team_id and team_id not in candidate_ids:
            candidate_ids.append(team_id)

    now = datetime.now(timezone.utc)
    years = (now.year - 1, now.year, now.year + 1)
    matches = {}

    for team_id in candidate_ids:
        for season in years:
            schedule = _cached_nhl_team_schedule(team_id, season)
            if not schedule:
                continue
            for event in schedule.get("events") or []:
                matched = _matched_result(
                    event,
                    away_team_name,
                    home_team_name,
                    "nhl",
                )
                if not matched:
                    continue
                event_id = str(matched.get("event_id") or "")
                event_time = _parse_event_time(event)
                if not event_id or not event_time:
                    continue
                matches[event_id] = (event_time, matched)

    if not matches:
        return None

    future = sorted(
        (item for item in matches.values() if item[0] >= now),
        key=lambda item: item[0],
    )
    if future:
        return future[0][1]

    # Only if there is no future meeting at all, use the most recent past one.
    past = sorted(matches.values(), key=lambda item: item[0], reverse=True)
    return past[0][1]


def find_event_by_teams(away_team_name, home_team_name, sport="ncaa", game_date=None):
    """Find a matchup in ESPN, using an exact date for NHL when supplied."""
    sport = (sport or "ncaa").lower()

    # Fast path: current scoreboard.
    try:
        current = legacy.get_scoreboard(sport)
        if current:
            for event in current.get("events", []):
                matched = _matched_result(event, away_team_name, home_team_name, sport)
                if matched:
                    return matched
    except Exception:
        pass

    if sport == "nhl":
        if game_date:
            try:
                if hasattr(game_date, "strftime"):
                    target_day = game_date
                else:
                    target_day = datetime.fromisoformat(str(game_date)).date()
            except Exception:
                target_day = None

            if target_day is not None:
                board = _cached_nhl_scoreboard(target_day)
                if board:
                    for event in board.get("events", []):
                        matched = _matched_result(
                            event,
                            away_team_name,
                            home_team_name,
                            sport,
                        )
                        if matched:
                            return matched
                # A selected NHL date is authoritative. Do not silently link
                # the same teams from another date.
                return None

        # Without an explicit date, use the full team schedule as a fallback
        # for automatic repair of previously saved unlinked games.
        scheduled = _find_nhl_event_from_team_schedule(
            away_team_name,
            home_team_name,
        )
        if scheduled:
            return scheduled

        from datetime import timedelta

        today = datetime.now(timezone.utc).date()
        board = _cached_nhl_scoreboard(
            today - timedelta(days=31),
            today + timedelta(days=120),
        )
        if board:
            for event in board.get("events", []):
                matched = _matched_result(event, away_team_name, home_team_name, sport)
                if matched:
                    return matched
        return None

    year = datetime.now(timezone.utc).year
    candidate_years = (year, year + 1, year - 1)
    for season in candidate_years:
        for season_type, weeks in _search_plan(sport):
            for week in weeks:
                board = _cached_scoreboard(sport, season, season_type, week)
                if not board:
                    continue
                for event in board.get("events", []):
                    matched = _matched_result(event, away_team_name, home_team_name, sport)
                    if matched:
                        return matched
    return None


def get_event_by_id(espn_event_id, sport="ncaa"):
    """Fetch a linked event directly instead of relying on today's scoreboard."""
    if not espn_event_id:
        return None
    try:
        response = _SESSION.get(
            _summary_url(sport),
            params={"event": str(espn_event_id)},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        header = data.get("header") or {}
        if header.get("competitions"):
            # ESPN summary keeps status/date on the competition, whereas the
            # legacy updater expects scoreboard-style top-level fields.
            competition = header.get("competitions", [{}])[0]
            event = dict(header)
            event["status"] = header.get("status") or competition.get("status") or {}
            event["date"] = header.get("date") or competition.get("date")
            return event
    except Exception:
        pass

    # Fallback to NHL team schedules/scoreboard if ESPN's summary endpoint is unavailable.
    if (sport or "ncaa").lower() == "nhl":
        teams = _cached_nhl_teams()
        for team in _iter_team_objects(teams):
            team_id = team.get("id")
            if team_id is None:
                continue
            for season in (
                datetime.now(timezone.utc).year - 1,
                datetime.now(timezone.utc).year,
                datetime.now(timezone.utc).year + 1,
            ):
                schedule = _cached_nhl_team_schedule(team_id, season)
                if not schedule:
                    continue
                for event in schedule.get("events") or []:
                    if str(event.get("id")) == str(espn_event_id):
                        return event

        from datetime import timedelta

        today = datetime.now(timezone.utc).date()
        board = _cached_nhl_scoreboard(
            today - timedelta(days=31),
            today + timedelta(days=120),
        )
        if board:
            for event in board.get("events", []):
                if str(event.get("id")) == str(espn_event_id):
                    return event
        return None

    year = datetime.now(timezone.utc).year
    for season in (year, year + 1, year - 1):
        for season_type, weeks in _search_plan(sport):
            for week in weeks:
                board = _cached_scoreboard(sport, season, season_type, week)
                if not board:
                    continue
                for event in board.get("events", []):
                    if str(event.get("id")) == str(espn_event_id):
                        return event
    return None


def find_first_kickoff(sport, season_type, week, season=None):
    """Return the first kickoff in a specific ESPN season/week as naive UTC."""
    season = season or datetime.now(timezone.utc).year
    board = _cached_scoreboard(sport, season, season_type, week)
    if not board:
        return None
    kickoffs = []
    for event in board.get("events", []):
        raw = event.get("date")
        if not raw:
            continue
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            kickoffs.append(parsed)
        except Exception:
            continue
    return min(kickoffs) if kickoffs else None


def install_espn_patches():
    """Patch the legacy module before pages/tasks import its functions."""
    legacy.find_event_by_teams = find_event_by_teams
    legacy.get_event_by_id = get_event_by_id
