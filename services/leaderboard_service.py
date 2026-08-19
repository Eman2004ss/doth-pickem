from database.db import SessionLocal

from database.models import (
    User,
    Leaderboard
)

from services.scoring_service import (
    calculate_user_points,
    calculate_user_correct_picks,
    calculate_user_total_picks
)


def update_user_leaderboard(user_id):

    db = SessionLocal()

    try:

        leaderboard = (
            db.query(Leaderboard)
            .filter(
                Leaderboard.user_id == user_id
            )
            .first()
        )

        if not leaderboard:
            return False

        leaderboard.total_points = (
            calculate_user_points(user_id)
        )

        leaderboard.correct_picks = (
            calculate_user_correct_picks(user_id)
        )

        leaderboard.total_picks = (
            calculate_user_total_picks(user_id)
        )

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_all_leaderboards():

    db = SessionLocal()

    try:

        users = db.query(User).all()

        for user in users:

            leaderboard = (
                db.query(Leaderboard)
                .filter(
                    Leaderboard.user_id == user.id
                )
                .first()
            )

            if not leaderboard:
                continue

            leaderboard.total_points = (
                calculate_user_points(
                    user.id
                )
            )

            leaderboard.correct_picks = (
                calculate_user_correct_picks(
                    user.id
                )
            )

            leaderboard.total_picks = (
                calculate_user_total_picks(
                    user.id
                )
            )

        db.commit()

        calculate_ranks()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def calculate_ranks():

    db = SessionLocal()

    try:

        leaderboard_rows = (
            db.query(Leaderboard)
            .order_by(
                Leaderboard.total_points.desc()
            )
            .all()
        )

        rank = 1

        for row in leaderboard_rows:

            row.rank = rank
            rank += 1

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def get_leaderboard():

    db = SessionLocal()

    try:

        return (
            db.query(Leaderboard)
            .order_by(
                Leaderboard.rank
            )
            .all()
        )

    finally:

        db.close()


def get_first_place():

    db = SessionLocal()

    try:

        return (
            db.query(Leaderboard)
            .order_by(
                Leaderboard.total_points.desc()
            )
            .first()
        )

    finally:

        db.close()


def get_user_rank(user_id):

    db = SessionLocal()

    try:

        leaderboard = (
            db.query(Leaderboard)
            .filter(
                Leaderboard.user_id == user_id
            )
            .first()
        )

        if not leaderboard:
            return None

        return leaderboard.rank

    finally:

        db.close()


def get_user_points(user_id):

    db = SessionLocal()

    try:

        leaderboard = (
            db.query(Leaderboard)
            .filter(
                Leaderboard.user_id == user_id
            )
            .first()
        )

        if not leaderboard:
            return 0

        return leaderboard.total_points

    finally:

        db.close()


def get_user_accuracy(user_id):

    db = SessionLocal()

    try:

        leaderboard = (
            db.query(Leaderboard)
            .filter(
                Leaderboard.user_id == user_id
            )
            .first()
        )

        if not leaderboard:
            return 0

        if leaderboard.total_picks == 0:
            return 0

        return round(
            (
                leaderboard.correct_picks
                / leaderboard.total_picks
            ) * 100,
            1
        )

    finally:

        db.close()