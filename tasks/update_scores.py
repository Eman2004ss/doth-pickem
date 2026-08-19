from database.db import SessionLocal

from database.models import Game

from services.espn_service import (
    update_game_from_espn
)


def run():

    db = SessionLocal()

    try:

        games = (
            db.query(Game)
            .filter(Game.completed == False)
            .filter(Game.espn_event_id.isnot(None))
            .all()
        )

        updated_count = 0

        for game in games:

            sport = (
                game.sport
                if game.sport
                else "ncaa"
            )

            success = update_game_from_espn(
                game.id,
                sport
            )

            if success:

                updated_count += 1

        return updated_count

    finally:

        db.close()


if __name__ == "__main__":

    updated = run()

    print(
        f"Updated scores for {updated} games."
    )