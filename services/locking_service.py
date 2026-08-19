from datetime import datetime

from database.db import SessionLocal

from database.models import (
    Game,
    Pick
)


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


def unlock_pick(pick_id):

    db = SessionLocal()

    try:

        pick = (
            db.query(Pick)
            .filter(Pick.id == pick_id)
            .first()
        )

        if not pick:
            return False

        pick.locked = False

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


def unlock_game_picks(game_id):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .filter(Pick.game_id == game_id)
            .all()
        )

        for pick in picks:
            pick.locked = False

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def should_lock_game(game):

    if not game.kickoff_time:
        return False

    return datetime.utcnow() >= game.kickoff_time


def lock_expired_games():

    db = SessionLocal()

    try:

        games = db.query(Game).all()

        locked_games = []

        for game in games:

            if not game.kickoff_time:
                continue

            if datetime.utcnow() < game.kickoff_time:
                continue

            picks = (
                db.query(Pick)
                .filter(Pick.game_id == game.id)
                .filter(Pick.locked == False)
                .all()
            )

            if not picks:
                continue

            for pick in picks:
                pick.locked = True

            locked_games.append(game.id)

        db.commit()

        return locked_games

    except Exception:

        db.rollback()

        return []

    finally:

        db.close()


def is_game_locked(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(Game.id == game_id)
            .first()
        )

        if not game:
            return False

        if not game.kickoff_time:
            return False

        return datetime.utcnow() >= game.kickoff_time

    finally:

        db.close()


def get_locked_games():

    db = SessionLocal()

    try:

        games = db.query(Game).all()

        locked_games = []

        for game in games:

            if not game.kickoff_time:
                continue

            if datetime.utcnow() >= game.kickoff_time:
                locked_games.append(game)

        return locked_games

    finally:

        db.close()