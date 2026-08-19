from database.db import SessionLocal

from database.models import (
    Game,
    Pick
)

from utils.constants import (
    TIER_POINTS
)


def get_game_points(tier):

    return TIER_POINTS.get(
        tier.upper(),
        0
    )


def score_completed_game(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(Game.id == game_id)
            .first()
        )

        if not game:
            return False

        if not game.completed:
            return False

        winner_id = game.winner_team_id

        picks = (
            db.query(Pick)
            .filter(Pick.game_id == game.id)
            .all()
        )

        points = get_game_points(
            game.tier
        )

        for pick in picks:

            if (
                pick.selected_team_id
                == winner_id
            ):
                pick.is_correct = True
                pick.points_awarded = points

            else:
                pick.is_correct = False
                pick.points_awarded = 0

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

        games = (
            db.query(Game)
            .filter(Game.completed == True)
            .all()
        )

        for game in games:

            winner_id = game.winner_team_id

            points = get_game_points(
                game.tier
            )

            picks = (
                db.query(Pick)
                .filter(
                    Pick.game_id == game.id
                )
                .all()
            )

            for pick in picks:

                if (
                    pick.selected_team_id
                    == winner_id
                ):
                    pick.is_correct = True
                    pick.points_awarded = points

                else:
                    pick.is_correct = False
                    pick.points_awarded = 0

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def calculate_user_points(user_id):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .filter(
                Pick.user_id == user_id
            )
            .all()
        )

        total = sum(
            pick.points_awarded
            for pick in picks
        )

        return total

    finally:

        db.close()


def calculate_user_correct_picks(user_id):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .filter(
                Pick.user_id == user_id
            )
            .all()
        )

        return sum(
            1
            for pick in picks
            if pick.is_correct
        )

    finally:

        db.close()


def calculate_user_total_picks(user_id):

    db = SessionLocal()

    try:

        return (
            db.query(Pick)
            .filter(
                Pick.user_id == user_id
            )
            .count()
        )

    finally:

        db.close()


def get_week_points(
    user_id,
    week_id
):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .join(
                Game,
                Pick.game_id == Game.id
            )
            .filter(
                Pick.user_id == user_id
            )
            .filter(
                Game.week_id == week_id
            )
            .all()
        )

        total = sum(
            pick.points_awarded
            for pick in picks
        )

        return total

    finally:

        db.close()


def get_week_correct_picks(
    user_id,
    week_id
):

    db = SessionLocal()

    try:

        picks = (
            db.query(Pick)
            .join(
                Game,
                Pick.game_id == Game.id
            )
            .filter(
                Pick.user_id == user_id
            )
            .filter(
                Game.week_id == week_id
            )
            .all()
        )

        return sum(
            1
            for pick in picks
            if pick.is_correct
        )

    finally:

        db.close()