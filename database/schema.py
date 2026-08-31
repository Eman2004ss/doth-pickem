import os

from database.db import SessionLocal, database_backend_name, engine
from database.models import Base, Leaderboard, Setting, User, Week
from database.xlsx_store import BUNDLED_EXCEL_PATH, import_xlsx_into_database


def create_database():
    """Create missing tables and initialize a brand-new database once.

    When ``DATABASE_URL`` points to Neon/PostgreSQL, that database is the
    durable source of truth. The bundled database.xlsx is imported only if the
    users table is empty, allowing the existing local data to migrate on the
    first deployment without overwriting future live data on redeploys.
    """

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing_user_count = db.query(User).count()
    finally:
        db.close()

    imported_from_excel = False

    should_seed_from_excel = (
        os.environ.get("SEED_FROM_XLSX", "true").strip().lower()
        not in {"0", "false", "no", "off"}
    )

    if existing_user_count == 0 and should_seed_from_excel:
        try:
            imported_from_excel = import_xlsx_into_database(
                engine,
                BUNDLED_EXCEL_PATH,
                replace_existing=False,
            )
        except Exception as error:
            print(f"Excel seed skipped because import failed: {error}")

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == "Hawes")
            .first()
        )

        if not existing_user and db.query(User).count() == 0:
            users = [
                User(
                    username="Hawes",
                    password="password",
                    is_admin=True,
                ),
                User(
                    username="Coleman",
                    password="password",
                    is_admin=False,
                ),
                User(
                    username="Jimbo",
                    password="password",
                    is_admin=False,
                ),
            ]

            db.add_all(users)
            db.commit()

        ensure_default_settings(db)
        ensure_leaderboard_rows(db)
        ensure_default_week(db)

        if imported_from_excel:
            print(
                "Seeded the new database from database/database.xlsx "
                f"using {database_backend_name()}."
            )
        else:
            print(
                "Database ready using "
                f"{database_backend_name()}. Existing data was preserved."
            )

    except Exception as error:
        db.rollback()
        print(f"Database initialization error: {error}")
        raise

    finally:
        db.close()


def ensure_leaderboard_rows(db):
    users = db.query(User).all()

    for user in users:
        existing_leaderboard = (
            db.query(Leaderboard)
            .filter(Leaderboard.user_id == user.id)
            .first()
        )

        if existing_leaderboard:
            continue

        leaderboard = Leaderboard(
            user_id=user.id,
            total_points=0,
            weekly_wins=0,
            correct_picks=0,
            total_picks=0,
            rank=0,
        )

        db.add(leaderboard)

    db.commit()


def ensure_default_settings(db):
    settings = {
        "current_week": "1",
        "season_name": "DothPick Football Season",
        "weekly_bonus_points": "5",
    }

    for setting_name, setting_value in settings.items():
        existing_setting = (
            db.query(Setting)
            .filter(Setting.setting_name == setting_name)
            .first()
        )

        if existing_setting:
            continue

        setting = Setting(
            setting_name=setting_name,
            setting_value=setting_value,
        )

        db.add(setting)

    db.commit()


def ensure_default_week(db):
    existing_week = (
        db.query(Week)
        .filter(Week.week_number == 1)
        .first()
    )

    if existing_week:
        return existing_week

    week = Week(
        week_number=1,
        active=True,
    )

    db.add(week)
    db.commit()
    db.refresh(week)

    return week


def reset_database():
    """Destructively reset whichever database DATABASE_URL points to."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_database()


if __name__ == "__main__":
    create_database()
