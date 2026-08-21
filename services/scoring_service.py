from database.db import SessionLocal
from database.models import Game, Pick, Week, WeeklyWinner
from services.special_scoring_service import get_special_total
from utils.constants import RIVALRY_GAME_POINTS, RIVALRY_WEEK_NUMBERS, TIER_POINTS


def is_rivalry_week_id(db, week_id):
    week = db.query(Week).filter(Week.id == week_id).first()
    return bool(week and week.week_number in RIVALRY_WEEK_NUMBERS)


def get_game_points(tier, week_number=None):
    """Return the exact points for S/A/B/C/D/F; legacy E remains one point."""
    if week_number in RIVALRY_WEEK_NUMBERS:
        return RIVALRY_GAME_POINTS
    normalized = (tier or "").upper()
    if normalized == "E":
        normalized = "F"
    return int(TIER_POINTS.get(normalized, 0))


def _points_for_game(db, game):
    week = db.query(Week).filter(Week.id == game.week_id).first()
    week_number = week.week_number if week else None
    return get_game_points(game.tier, week_number)


def score_completed_game(game_id):
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game or not game.completed:
            return False
        winner_id = game.winner_team_id
        points = _points_for_game(db, game)
        picks = db.query(Pick).filter(Pick.game_id == game.id).all()
        for pick in picks:
            correct = winner_id is not None and pick.selected_team_id == winner_id
            pick.is_correct = bool(correct)
            pick.points_awarded = points if correct else 0
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def score_all_completed_games():
    db = SessionLocal()
    try:
        games = db.query(Game).filter(Game.completed == True).all()
        for game in games:
            winner_id = game.winner_team_id
            points = _points_for_game(db, game)
            for pick in db.query(Pick).filter(Pick.game_id == game.id).all():
                correct = winner_id is not None and pick.selected_team_id == winner_id
                pick.is_correct = bool(correct)
                pick.points_awarded = points if correct else 0
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def calculate_user_points(user_id):
    """Season total = game picks + weekly bonuses + special-pick points/bonuses."""
    db = SessionLocal()
    try:
        game_points = sum(
            int(pick.points_awarded or 0)
            for pick in db.query(Pick).filter(Pick.user_id == user_id).all()
        )
        weekly_bonus = sum(
            int(row.bonus_points or 0)
            for row in db.query(WeeklyWinner).filter(WeeklyWinner.user_id == user_id).all()
        )
    finally:
        db.close()
    return game_points + weekly_bonus + get_special_total(user_id)


def calculate_user_correct_picks(user_id):
    db = SessionLocal()
    try:
        picks = db.query(Pick).filter(Pick.user_id == user_id).all()
        return sum(1 for pick in picks if pick.is_correct)
    finally:
        db.close()


def calculate_user_total_picks(user_id):
    db = SessionLocal()
    try:
        return db.query(Pick).filter(Pick.user_id == user_id).count()
    finally:
        db.close()


def get_week_points(user_id, week_id):
    db = SessionLocal()
    try:
        picks = (
            db.query(Pick)
            .join(Game, Pick.game_id == Game.id)
            .filter(Pick.user_id == user_id)
            .filter(Game.week_id == week_id)
            .all()
        )
        return sum(int(pick.points_awarded or 0) for pick in picks)
    finally:
        db.close()


def get_week_correct_picks(user_id, week_id):
    db = SessionLocal()
    try:
        picks = (
            db.query(Pick)
            .join(Game, Pick.game_id == Game.id)
            .filter(Pick.user_id == user_id)
            .filter(Game.week_id == week_id)
            .all()
        )
        return sum(1 for pick in picks if pick.is_correct)
    finally:
        db.close()
