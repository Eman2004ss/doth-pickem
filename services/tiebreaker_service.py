from datetime import datetime

from database.db import SessionLocal
from database.models import Game
from database.extra_models import TiebreakerPick


def _game_one(db, week_id):
    return (
        db.query(Game)
        .filter(Game.week_id == week_id)
        .order_by(Game.game_number.asc(), Game.id.asc())
        .first()
    )


def get_tiebreaker(user_id, week_id):
    db = SessionLocal()
    try:
        return (
            db.query(TiebreakerPick)
            .filter(TiebreakerPick.user_id == user_id)
            .filter(TiebreakerPick.week_id == week_id)
            .first()
        )
    finally:
        db.close()


def is_tiebreaker_locked(week_id):
    db = SessionLocal()
    try:
        game = _game_one(db, week_id)
        if not game or not game.kickoff_time:
            return False
        kickoff = game.kickoff_time
        if getattr(kickoff, "tzinfo", None) is not None:
            kickoff = kickoff.replace(tzinfo=None)
        return datetime.utcnow() >= kickoff
    finally:
        db.close()


def save_tiebreaker(user_id, week_id, predicted_total):
    try:
        predicted_total = int(predicted_total)
    except (TypeError, ValueError):
        return False, "Enter a whole-number total."
    if predicted_total < 0 or predicted_total > 250:
        return False, "Tiebreaker must be between 0 and 250 points."
    if is_tiebreaker_locked(week_id):
        return False, "The tiebreaker locked at kickoff of Game 1."

    db = SessionLocal()
    try:
        row = (
            db.query(TiebreakerPick)
            .filter(TiebreakerPick.user_id == user_id)
            .filter(TiebreakerPick.week_id == week_id)
            .first()
        )
        if not row:
            row = TiebreakerPick(
                user_id=user_id,
                week_id=week_id,
                predicted_total=predicted_total,
            )
            db.add(row)
        else:
            row.predicted_total = predicted_total
            row.updated_at = datetime.utcnow()
        db.commit()
        return True, "Tiebreaker saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save tiebreaker: {error}"
    finally:
        db.close()


def actual_game_one_total(week_id):
    db = SessionLocal()
    try:
        game = _game_one(db, week_id)
        if not game or not game.completed:
            return None
        return int(game.home_score or 0) + int(game.away_score or 0)
    finally:
        db.close()


def tiebreaker_deviation(user_id, week_id):
    actual = actual_game_one_total(week_id)
    if actual is None:
        return None
    row = get_tiebreaker(user_id, week_id)
    if not row:
        return None
    return abs(int(row.predicted_total) - actual)


def lock_expired_tiebreakers():
    db = SessionLocal()
    try:
        rows = db.query(TiebreakerPick).filter(TiebreakerPick.locked == False).all()
        changed = 0
        for row in rows:
            game = _game_one(db, row.week_id)
            if not game or not game.kickoff_time:
                continue
            kickoff = game.kickoff_time
            if getattr(kickoff, "tzinfo", None) is not None:
                kickoff = kickoff.replace(tzinfo=None)
            if datetime.utcnow() >= kickoff:
                row.locked = True
                changed += 1
        db.commit()
        return changed
    except Exception:
        db.rollback()
        return 0
    finally:
        db.close()
