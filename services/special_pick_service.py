from datetime import datetime, timezone
import re

from database.db import SessionLocal
from database.models import Game, Team, Week
from database.extra_models import SpecialLock, SpecialPick
from services.espn_compat import find_first_kickoff


# Automatic lock anchors.  Manual admin overrides in special_locks take priority.
# CFB postseason conference picks lock at the first conference-championship-week
# kickoff (ESPN college regular-season Week 15). NFL postseason locks at the
# first playoff game (ESPN postseason Week 1).
LOCK_ANCHORS = {
    ("cfb_conference", "preseason"): ("ncaa", 0, 2),
    ("cfb_conference", "midseason"): ("ncaa", 10, 2),
    ("cfb_conference", "postseason"): ("ncaa", 15, 2),
    ("cfp_preseason", "preseason"): ("ncaa", 0, 2),
    ("nfl_preseason", "preseason"): ("nfl", 1, 2),
    ("nfl_champion", "midseason"): ("nfl", 10, 2),
    ("nfl_champion", "postseason"): ("nfl", 1, 3),
    ("nfl_division", "preseason"): ("nfl", 1, 2),
}


NFL_CONFERENCE = {
    "Buffalo Bills": "AFC", "Miami Dolphins": "AFC", "New England Patriots": "AFC", "New York Jets": "AFC",
    "Baltimore Ravens": "AFC", "Cincinnati Bengals": "AFC", "Cleveland Browns": "AFC", "Pittsburgh Steelers": "AFC",
    "Houston Texans": "AFC", "Indianapolis Colts": "AFC", "Jacksonville Jaguars": "AFC", "Tennessee Titans": "AFC",
    "Denver Broncos": "AFC", "Kansas City Chiefs": "AFC", "Las Vegas Raiders": "AFC", "Los Angeles Chargers": "AFC",
    "Dallas Cowboys": "NFC", "New York Giants": "NFC", "Philadelphia Eagles": "NFC", "Washington Commanders": "NFC",
    "Chicago Bears": "NFC", "Detroit Lions": "NFC", "Green Bay Packers": "NFC", "Minnesota Vikings": "NFC",
    "Atlanta Falcons": "NFC", "Carolina Panthers": "NFC", "New Orleans Saints": "NFC", "Tampa Bay Buccaneers": "NFC",
    "Arizona Cardinals": "NFC", "Los Angeles Rams": "NFC", "San Francisco 49ers": "NFC", "Seattle Seahawks": "NFC",
}

NFL_DIVISIONS = {
    "AFC East": ["Buffalo Bills", "Miami Dolphins", "New England Patriots", "New York Jets"],
    "AFC North": ["Baltimore Ravens", "Cincinnati Bengals", "Cleveland Browns", "Pittsburgh Steelers"],
    "AFC South": ["Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Tennessee Titans"],
    "AFC West": ["Denver Broncos", "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers"],
    "NFC East": ["Dallas Cowboys", "New York Giants", "Philadelphia Eagles", "Washington Commanders"],
    "NFC North": ["Chicago Bears", "Detroit Lions", "Green Bay Packers", "Minnesota Vikings"],
    "NFC South": ["Atlanta Falcons", "Carolina Panthers", "New Orleans Saints", "Tampa Bay Buccaneers"],
    "NFC West": ["Arizona Cardinals", "Los Angeles Rams", "San Francisco 49ers", "Seattle Seahawks"],
}

CFB_CONFERENCES = ["Big Ten", "SEC", "ACC", "Big 12"]


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def _naive_utc(value):
    if value is None:
        return None
    if getattr(value, "tzinfo", None) is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _db_anchor_kickoff(sport, week_number):
    db = SessionLocal()
    try:
        week = db.query(Week).filter(Week.week_number == int(week_number)).first()
        if not week:
            return None
        query = db.query(Game).filter(Game.week_id == week.id).filter(Game.kickoff_time.isnot(None))
        games = query.all()
        games = [g for g in games if (g.sport or "ncaa").lower() == sport]
        if not games:
            return None
        return min(_naive_utc(g.kickoff_time) for g in games)
    finally:
        db.close()


def get_special_lock_time(category, period):
    db = SessionLocal()
    try:
        override = (
            db.query(SpecialLock)
            .filter(SpecialLock.category == category)
            .filter(SpecialLock.period == period)
            .first()
        )
        if override and override.lock_at:
            return _naive_utc(override.lock_at)
    finally:
        db.close()

    anchor = LOCK_ANCHORS.get((category, period))
    if not anchor:
        return None
    sport, week_number, season_type = anchor

    # For regular-season anchors, the board's own kickoff time is preferred.
    if season_type == 2:
        db_time = _db_anchor_kickoff(sport, week_number)
        if db_time:
            return db_time

    try:
        return find_first_kickoff(sport, season_type, week_number)
    except Exception:
        return None


def is_special_locked(category, period):
    db = SessionLocal()
    try:
        override = (
            db.query(SpecialLock)
            .filter(SpecialLock.category == category)
            .filter(SpecialLock.period == period)
            .first()
        )
        if override and override.force_locked:
            return True
    finally:
        db.close()

    lock_time = get_special_lock_time(category, period)
    return bool(lock_time and datetime.utcnow() >= lock_time)


def set_special_lock(category, period, lock_at=None, force_locked=False):
    db = SessionLocal()
    try:
        row = (
            db.query(SpecialLock)
            .filter(SpecialLock.category == category)
            .filter(SpecialLock.period == period)
            .first()
        )
        if not row:
            row = SpecialLock(category=category, period=period)
            db.add(row)
        row.lock_at = _naive_utc(lock_at)
        row.force_locked = bool(force_locked)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_special_pick(user_id, category, period, slot):
    db = SessionLocal()
    try:
        return (
            db.query(SpecialPick)
            .filter(SpecialPick.user_id == user_id)
            .filter(SpecialPick.category == category)
            .filter(SpecialPick.period == period)
            .filter(SpecialPick.slot == slot)
            .first()
        )
    finally:
        db.close()


def get_special_picks(user_id=None, category=None, period=None):
    db = SessionLocal()
    try:
        query = db.query(SpecialPick)
        if user_id is not None:
            query = query.filter(SpecialPick.user_id == user_id)
        if category is not None:
            query = query.filter(SpecialPick.category == category)
        if period is not None:
            query = query.filter(SpecialPick.period == period)
        return query.order_by(SpecialPick.category, SpecialPick.period, SpecialPick.slot).all()
    finally:
        db.close()


def _upsert_pick(db, user_id, category, period, slot, selection, rank=None):
    row = (
        db.query(SpecialPick)
        .filter(SpecialPick.user_id == user_id)
        .filter(SpecialPick.category == category)
        .filter(SpecialPick.period == period)
        .filter(SpecialPick.slot == slot)
        .first()
    )
    if not row:
        row = SpecialPick(
            user_id=user_id,
            category=category,
            period=period,
            slot=slot,
            selection=selection,
            rank=rank,
        )
        db.add(row)
    else:
        row.selection = selection
        row.rank = rank
        row.updated_at = datetime.utcnow()
    return row


def save_special_pick(user_id, category, period, slot, selection, rank=None):
    if is_special_locked(category, period):
        return False, "These picks are locked."
    selection = (selection or "").strip()
    if not selection:
        return False, "Choose a team first."

    db = SessionLocal()
    try:
        _upsert_pick(db, user_id, category, period, slot, selection, rank)
        db.commit()
        return True, "Pick saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save pick: {error}"
    finally:
        db.close()


def save_ranked_picks(user_id, category, period, selections):
    """Save a complete ranked list atomically; selections is rank-ordered."""
    if is_special_locked(category, period):
        return False, "These picks are locked."
    values = [(value or "").strip() for value in selections]
    if any(not value for value in values):
        return False, "Complete every ranked team before saving."
    if len({_norm(value) for value in values}) != len(values):
        return False, "Each ranked team must be different."

    if category == "nfl_preseason":
        conferences = [NFL_CONFERENCE.get(value) for value in values]
        if conferences.count("AFC") != 2 or conferences.count("NFC") != 2:
            return False, "NFL preseason picks must contain exactly 2 AFC and 2 NFC teams."

    db = SessionLocal()
    try:
        for index, value in enumerate(values, start=1):
            _upsert_pick(db, user_id, category, period, f"rank{index}", value, index)
        db.commit()
        return True, "Ranked picks saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save picks: {error}"
    finally:
        db.close()


def save_conference_pick(user_id, period, conference, selection):
    """CFB conference guesses cannot repeat the same team across periods."""
    if is_special_locked("cfb_conference", period):
        return False, "These picks are locked."
    selection = (selection or "").strip()
    if not selection:
        return False, "Choose a team first."

    db = SessionLocal()
    try:
        existing = (
            db.query(SpecialPick)
            .filter(SpecialPick.user_id == user_id)
            .filter(SpecialPick.category == "cfb_conference")
            .filter(SpecialPick.slot == conference)
            .filter(SpecialPick.period != period)
            .all()
        )
        if any(_norm(row.selection) == _norm(selection) for row in existing):
            return False, "You cannot use the same team twice for this conference."
        _upsert_pick(db, user_id, "cfb_conference", period, conference, selection)
        db.commit()
        return True, "Conference pick saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save pick: {error}"
    finally:
        db.close()


def get_team_names(sport=None):
    db = SessionLocal()
    try:
        query = db.query(Team)
        if sport:
            query = query.filter(Team.sport == sport)
        return sorted({team.team_name for team in query.all() if team.team_name})
    finally:
        db.close()


def get_nfl_teams(conference=None):
    if conference:
        return sorted(team for team, conf in NFL_CONFERENCE.items() if conf == conference)
    return sorted(NFL_CONFERENCE)

from utils.team_data import NCAA_CONFERENCES

def get_cfb_conference_teams(conference):
    return NCAA_CONFERENCES.get(conference, [])


def lock_expired_special_picks():
    db = SessionLocal()
    try:
        rows = db.query(SpecialPick).filter(SpecialPick.locked == False).all()
        changed = 0
        cache = {}
        for row in rows:
            key = (row.category, row.period)
            if key not in cache:
                cache[key] = is_special_locked(*key)
            if cache[key]:
                row.locked = True
                changed += 1
        db.commit()
        return changed
    except Exception:
        db.rollback()
        return 0
    finally:
        db.close()
