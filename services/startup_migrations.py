"""Small, idempotent startup migrations for the 2026 scoring update."""

from database.db import SessionLocal
from database.models import Game
from services.week3_texas_tech_houston_migration import run as restore_week3_texas_tech_houston


def run_startup_migrations():
    """Run safe repeatable migrations without replacing existing picks."""
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

    restore_week3_texas_tech_houston()
