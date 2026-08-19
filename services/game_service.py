from database.db import SessionLocal

from database.models import (
    Game,
    Team
)


def create_game(
    week_id,
    game_number,
    tier,
    home_team_id,
    away_team_id,
    kickoff_time=None,
    espn_event_id=None,
    sport="ncaa"
):

    db = SessionLocal()

    try:

        existing_game = (
            db.query(Game)
            .filter(
                Game.week_id == week_id
            )
            .filter(
                Game.game_number == game_number
            )
            .first()
        )

        if existing_game:

            existing_game.tier = tier
            existing_game.home_team_id = home_team_id
            existing_game.away_team_id = away_team_id
            existing_game.kickoff_time = kickoff_time
            existing_game.espn_event_id = espn_event_id

            if hasattr(
                existing_game,
                "sport"
            ):
                existing_game.sport = sport

            db.commit()

            db.refresh(
                existing_game
            )

            return existing_game

        game = Game(
            week_id=week_id,
            game_number=game_number,
            tier=tier,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            kickoff_time=kickoff_time,
            espn_event_id=espn_event_id
        )

        if hasattr(
            game,
            "sport"
        ):
            game.sport = sport

        db.add(game)

        db.commit()

        db.refresh(game)

        return game

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


def get_game_by_id(game_id):

    db = SessionLocal()

    try:

        return (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

    finally:

        db.close()


def get_games_by_week(week_id):

    db = SessionLocal()

    try:

        return (
            db.query(Game)
            .filter(
                Game.week_id == week_id
            )
            .order_by(
                Game.game_number
            )
            .all()
        )

    finally:

        db.close()


def get_game_by_week_and_number(
    week_id,
    game_number
):

    db = SessionLocal()

    try:

        return (
            db.query(Game)
            .filter(
                Game.week_id == week_id
            )
            .filter(
                Game.game_number == game_number
            )
            .first()
        )

    finally:

        db.close()


def game_exists(
    week_id,
    game_number
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.week_id == week_id
            )
            .filter(
                Game.game_number == game_number
            )
            .first()
        )

        return game is not None

    finally:

        db.close()


def update_game(
    game_id,
    tier=None,
    home_team_id=None,
    away_team_id=None,
    kickoff_time=None,
    espn_event_id=None,
    sport=None
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        if tier is not None:
            game.tier = tier

        if home_team_id is not None:
            game.home_team_id = home_team_id

        if away_team_id is not None:
            game.away_team_id = away_team_id

        if kickoff_time is not None:
            game.kickoff_time = kickoff_time

        if espn_event_id is not None:
            game.espn_event_id = espn_event_id

        if (
            sport is not None
            and
            hasattr(
                game,
                "sport"
            )
        ):
            game.sport = sport

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_scores(
    game_id,
    home_score,
    away_score
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        game.home_score = home_score
        game.away_score = away_score

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_game_status(
    game_id,
    status,
    quarter=None,
    game_clock=None
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        game.game_status = status
        game.quarter = quarter
        game.game_clock = game_clock

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def complete_game(
    game_id,
    winner_team_id
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        game.completed = True
        game.winner_team_id = winner_team_id
        game.game_status = "Final"

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def determine_and_complete_game(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        if game.home_score > game.away_score:

            game.winner_team_id = game.home_team_id

        elif game.away_score > game.home_score:

            game.winner_team_id = game.away_team_id

        else:

            game.winner_team_id = None

        game.completed = True
        game.game_status = "Final"

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_espn_event_id(
    game_id,
    espn_event_id
):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        game.espn_event_id = espn_event_id

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def get_home_team(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return None

        return (
            db.query(Team)
            .filter(
                Team.id == game.home_team_id
            )
            .first()
        )

    finally:

        db.close()


def get_away_team(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return None

        return (
            db.query(Team)
            .filter(
                Team.id == game.away_team_id
            )
            .first()
        )

    finally:

        db.close()


def get_winner_team(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return None

        if not game.winner_team_id:
            return None

        return (
            db.query(Team)
            .filter(
                Team.id == game.winner_team_id
            )
            .first()
        )

    finally:

        db.close()


def delete_game(game_id):

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        db.delete(game)

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()