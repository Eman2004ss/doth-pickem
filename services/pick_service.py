from datetime import datetime

from database.db import SessionLocal

from database.models import (
    Pick,
    Game
)


def create_pick(
    user_id,
    game_id,
    selected_team_id
):

    db = SessionLocal()

    try:

        existing_pick = (
            db.query(Pick)
            .filter(Pick.user_id == user_id)
            .filter(Pick.game_id == game_id)
            .first()
        )

        if existing_pick:
            return None

        pick = Pick(
            user_id=user_id,
            game_id=game_id,
            selected_team_id=selected_team_id,
            locked=False
        )

        db.add(pick)

        db.commit()

        db.refresh(pick)

        return pick

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


def get_pick_by_id(pick_id):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .filter(Pick.id == pick_id)
            .first()
        )

    finally:

        db.close()


def get_user_pick(
    user_id,
    game_id
):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .filter(Pick.user_id == user_id)
            .filter(Pick.game_id == game_id)
            .first()
        )

    finally:

        db.close()


def get_user_picks(user_id):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .filter(Pick.user_id == user_id)
            .all()
        )

    finally:

        db.close()


def get_game_picks(game_id):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .filter(Pick.game_id == game_id)
            .all()
        )

    finally:

        db.close()


def get_week_picks(week_id):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .join(Game)
            .filter(Game.week_id == week_id)
            .all()
        )

    finally:

        db.close()


def update_pick(
    user_id,
    game_id,
    selected_team_id
):

    db = SessionLocal()

    try:

        pick = (
            db.query(Pick)
            .filter(Pick.user_id == user_id)
            .filter(Pick.game_id == game_id)
            .first()
        )

        if not pick:
            return False

        if pick.locked:
            return False

        pick.selected_team_id = selected_team_id
        pick.updated_at = datetime.utcnow()

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def lock_pick(pick_id):

    db = SessionLocal()

    try:

        pick = (
            db.query(Pick)
            .filter(Pick.id == pick_id)
            .first()
        )

        if not pick:
            return False

        pick.locked = True

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def lock_game_picks(game_id):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .filter(Pick.game_id == game_id)
            .all()
        )

        for pick in picks:
            pick.locked = True

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def mark_pick_result(
    pick_id,
    is_correct,
    points_awarded
):

    db = SessionLocal()

    try:

        pick = (
            db.query(Pick)
            .filter(Pick.id == pick_id)
            .first()
        )

        if not pick:
            return False

        pick.is_correct = is_correct
        pick.points_awarded = points_awarded

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def delete_pick(pick_id):

    db = SessionLocal()

    try:

        pick = (
            db.query(Pick)
            .filter(Pick.id == pick_id)
            .first()
        )

        if not pick:
            return False

        # Locked picks are part of the permanent weekly history.
        if pick.locked:
            return False

        db.delete(pick)

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()