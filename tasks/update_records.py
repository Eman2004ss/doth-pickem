from database.db import SessionLocal

from database.models import Team

from services.espn_service import (
    update_team_record
)


def run():

    db = SessionLocal()

    try:

        teams = (
            db.query(Team)
            .filter(Team.espn_team_id.isnot(None))
            .all()
        )

        updated_count = 0

        for team in teams:

            if not team.record:
                continue

            success = update_team_record(
                team.id,
                team.record
            )

            if success:
                updated_count += 1

        return updated_count

    finally:

        db.close()


if __name__ == "__main__":

    updated = run()

    print(
        f"Updated records for {updated} teams."
    )