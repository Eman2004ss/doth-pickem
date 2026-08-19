from database.db import SessionLocal

from database.models import (
    Game,
    Week,
    User,
    WeeklyWinner,
    Leaderboard
)

from services.scoring_service import (
    score_completed_game,
    get_week_points
)

from services.leaderboard_service import (
    update_all_leaderboards
)

from utils.constants import (
    WEEKLY_WIN_BONUS
)


def score_completed_games():

    db = SessionLocal()

    try:

        games = (
            db.query(Game)
            .filter(Game.completed == True)
            .all()
        )

        scored_count = 0

        for game in games:

            success = score_completed_game(
                game.id
            )

            if success:
                scored_count += 1

        return scored_count

    finally:

        db.close()


def week_is_complete(week_id):

    db = SessionLocal()

    try:

        games = (
            db.query(Game)
            .filter(Game.week_id == week_id)
            .all()
        )

        if not games:
            return False

        for game in games:

            if not game.completed:
                return False

        return True

    finally:

        db.close()


def calculate_week_winner(week_id):

    db = SessionLocal()

    try:

        if not week_is_complete(
            week_id
        ):

            return None

        existing_winner = (
            db.query(WeeklyWinner)
            .filter(
                WeeklyWinner.week_id == week_id
            )
            .first()
        )

        if existing_winner:
            return existing_winner

        users = db.query(User).all()

        if not users:
            return None

        highest_points = -1
        winning_users = []

        for user in users:

            points = get_week_points(
                user.id,
                week_id
            )

            if points > highest_points:

                highest_points = points
                winning_users = [
                    user
                ]

            elif points == highest_points:

                winning_users.append(
                    user
                )

        if not winning_users:
            return None

        bonus_per_user = WEEKLY_WIN_BONUS

        created_winners = []

        for winning_user in winning_users:

            weekly_winner = WeeklyWinner(
                week_id=week_id,
                user_id=winning_user.id,
                bonus_points=bonus_per_user
            )

            db.add(
                weekly_winner
            )

            leaderboard = (
                db.query(Leaderboard)
                .filter(
                    Leaderboard.user_id
                    ==
                    winning_user.id
                )
                .first()
            )

            if leaderboard:

                leaderboard.total_points += (
                    bonus_per_user
                )

                leaderboard.weekly_wins += 1

            created_winners.append(
                weekly_winner
            )

        db.commit()

        return created_winners

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


def calculate_all_week_winners():

    db = SessionLocal()

    try:

        weeks = db.query(Week).all()

        calculated_count = 0

        for week in weeks:

            result = calculate_week_winner(
                week.id
            )

            if result:
                calculated_count += 1

        return calculated_count

    finally:

        db.close()


def run():

    scored_games = score_completed_games()

    calculate_all_week_winners()

    update_all_leaderboards()

    return scored_games


if __name__ == "__main__":

    total_scored = run()

    print(
        f"Scored {total_scored} completed games."
    )