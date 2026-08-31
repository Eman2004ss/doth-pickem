"""Small, idempotent startup migrations for the 2026 scoring update."""

from database.db import SessionLocal
from database.models import Game


def run_startup_migrations():
    """Rename legacy one-point E-tier rows to F without changing their value."""
    db = SessionLocal()
    try:
        db.query(Game).filter(Game.tier == "E").update(
            {Game.tier: "F"},
            synchronize_session=False,
        )
        db.commit()
    except Exception as error:
        db.rollback()
        print(f"startup migration error: {error}")
    finally:
        db.close()
