"""One-time database migration/verification helper.

Usage:
    1. Set DATABASE_URL to your Neon connection string.
    2. Run: python migrate_to_neon.py

The script creates the schema and, if the target database is empty, imports the
bundled database/database.xlsx snapshot. It will not overwrite a populated
Neon database.
"""

from database.db import SessionLocal, database_backend_name
from database.models import Game, Pick, Team, User, Week
from database.schema import create_database


def main():
    create_database()

    db = SessionLocal()
    try:
        print(f"Backend: {database_backend_name()}")
        print(f"Users: {db.query(User).count()}")
        print(f"Teams: {db.query(Team).count()}")
        print(f"Weeks: {db.query(Week).count()}")
        print(f"Games: {db.query(Game).count()}")
        print(f"Picks: {db.query(Pick).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
