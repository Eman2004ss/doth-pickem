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


def _league_path(sport):
    return "nfl" if (sport or "ncaa").lower() == "nfl" else "college-football"


def _scoreboard_url(sport):
    return (
        "https://site.api.espn.com/apis/site/v2/sports/football/"
        f"{_league_path(sport)}/scoreboard"
    )


def _summary_url(sport):
    return (
        "https://site.api.espn.com/apis/site/v2/sports/football/"
        f"{_league_path(sport)}/summary"
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


def _event_matches(event, away_name, home_name):
    away, home = _event_competitors(event)
    if not away or not home:
        return False
    away_team = away.get("team") or {}
    home_team = home.get("team") or {}

    # Keep home/away orientation strict. The rest of the app stores ESPN's
    # home score against Game.home_team_id and ESPN's away score against
    # Game.away_team_id; accepting a reversed matchup here could silently
    # attach scores to the wrong database teams.
    return _team_matches(away_name, away_team) and _team_matches(home_name, home_team)


def _search_plan(sport):
    if (sport or "ncaa").lower() == "nfl":
        # preseason, regular season, postseason
        return [(1, range(1, 6)), (2, range(1, 19)), (3, range(1, 7))]
    # College schedules occasionally expose Week 0 and can extend through
    # conference championships/postseason.
    return [(2, range(0, 17)), (3, range(1, 8))]


def find_event_by_teams(away_team_name, home_team_name, sport="ncaa"):
    """Find a matchup anywhere in the relevant ESPN season schedule."""
    sport = (sport or "ncaa").lower()
    year = datetime.now(timezone.utc).year
    candidate_years = (year, year + 1, year - 1)

    # Fast path: keep the legacy current-scoreboard lookup first.
    try:
        current = legacy.get_scoreboard(sport)
        if current:
            for event in current.get("events", []):
                if _event_matches(event, away_team_name, home_team_name):
                    return _event_result(event, sport)
    except Exception:
        pass

    for season in candidate_years:
        for season_type, weeks in _search_plan(sport):
            for week in weeks:
                board = _cached_scoreboard(sport, season, season_type, week)
                if not board:
                    continue
                for event in board.get("events", []):
                    if _event_matches(event, away_team_name, home_team_name):
                        return _event_result(event, sport)
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

    # Fallback to a season scan if ESPN's summary endpoint is unavailable.
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
