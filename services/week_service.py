from database.db import SessionLocal

from database.models import (
    Week,
    Setting,
    Game,
    Pick
)


def create_week(week_number):

    db = SessionLocal()

    try:

        existing_week = (
            db.query(Week)
            .filter(
                Week.week_number == week_number
            )
            .first()
        )

        if existing_week:
            return existing_week

        existing_weeks_count = (
            db.query(Week)
            .count()
        )

        week = Week(
            week_number=week_number,
            active=existing_weeks_count == 0
        )

        db.add(week)

        db.commit()

        db.refresh(week)

        return week

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


def get_week_by_id(week_id):

    db = SessionLocal()

    try:

        return (
            db.query(Week)
            .filter(
                Week.id == week_id
            )
            .first()
        )

    finally:

        db.close()


def get_week_by_number(week_number):

    db = SessionLocal()

    try:

        return (
            db.query(Week)
            .filter(
                Week.week_number == week_number
            )
            .first()
        )

    finally:

        db.close()


def get_all_weeks():

    db = SessionLocal()

    try:

        return (
            db.query(Week)
            .order_by(
                Week.week_number
            )
            .all()
        )

    finally:

        db.close()


def get_active_week():

    db = SessionLocal()

    try:

        active_week = (
            db.query(Week)
            .filter(
                Week.active == True
            )
            .first()
        )

        if active_week:
            return active_week

        fallback_week = (
            db.query(Week)
            .order_by(
                Week.week_number
            )
            .first()
        )

        if fallback_week:

            fallback_week.active = True

            db.commit()

            db.refresh(fallback_week)

            return fallback_week

        return None

    finally:

        db.close()


def set_active_week(week_id):

    db = SessionLocal()

    try:

        week = (
            db.query(Week)
            .filter(
                Week.id == week_id
            )
            .first()
        )

        if not week:
            return False

        all_weeks = db.query(Week).all()

        for existing_week in all_weeks:

            existing_week.active = False

        week.active = True

        current_week_setting = (
            db.query(Setting)
            .filter(
                Setting.setting_name == "current_week"
            )
            .first()
        )

        if current_week_setting:

            current_week_setting.setting_value = str(
                week.week_number
            )

        else:

            current_week_setting = Setting(
                setting_name="current_week",
                setting_value=str(
                    week.week_number
                )
            )

            db.add(
                current_week_setting
            )

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def set_active_week_by_number(week_number):

    db = SessionLocal()

    try:

        week = (
            db.query(Week)
            .filter(
                Week.week_number == week_number
            )
            .first()
        )

        if not week:
            return False

        all_weeks = db.query(Week).all()

        for existing_week in all_weeks:

            existing_week.active = False

        week.active = True

        current_week_setting = (
            db.query(Setting)
            .filter(
                Setting.setting_name == "current_week"
            )
            .first()
        )

        if current_week_setting:

            current_week_setting.setting_value = str(
                week.week_number
            )

        else:

            current_week_setting = Setting(
                setting_name="current_week",
                setting_value=str(
                    week.week_number
                )
            )

            db.add(
                current_week_setting
            )

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_week_number(
    week_id,
    new_week_number
):

    db = SessionLocal()

    try:

        week = (
            db.query(Week)
            .filter(
                Week.id == week_id
            )
            .first()
        )

        if not week:
            return False

        duplicate_week = (
            db.query(Week)
            .filter(
                Week.week_number == new_week_number
            )
            .first()
        )

        if (
            duplicate_week
            and
            duplicate_week.id != week_id
        ):
            return False

        week.week_number = new_week_number

        if week.active:

            current_week_setting = (
                db.query(Setting)
                .filter(
                    Setting.setting_name == "current_week"
                )
                .first()
            )

            if current_week_setting:

                current_week_setting.setting_value = str(
                    new_week_number
                )

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def delete_week(week_id):

    db = SessionLocal()

    try:

        week = (
            db.query(Week)
            .filter(
                Week.id == week_id
            )
            .first()
        )

        if not week:
            return False

        # A week becomes permanent once any pick is locked or a game completes.
        has_locked_picks = (
            db.query(Pick)
            .join(Game, Pick.game_id == Game.id)
            .filter(Game.week_id == week.id)
            .filter(Pick.locked == True)
            .first()
            is not None
        )

        has_completed_games = (
            db.query(Game)
            .filter(Game.week_id == week.id)
            .filter(Game.completed == True)
            .first()
            is not None
        )

        if has_locked_picks or has_completed_games:
            return False

        was_active = week.active

        db.delete(week)

        db.commit()

        if was_active:

            next_week = (
                db.query(Week)
                .order_by(
                    Week.week_number
                )
                .first()
            )

            if next_week:

                next_week.active = True

                current_week_setting = (
                    db.query(Setting)
                    .filter(
                        Setting.setting_name == "current_week"
                    )
                    .first()
                )

                if current_week_setting:

                    current_week_setting.setting_value = str(
                        next_week.week_number
                    )

                db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def week_exists(week_number):

    db = SessionLocal()

    try:

        week = (
            db.query(Week)
            .filter(
                Week.week_number == week_number
            )
            .first()
        )

        return week is not None

    finally:

        db.close()


def get_current_week_number():

    db = SessionLocal()

    try:

        setting = (
            db.query(Setting)
            .filter(
                Setting.setting_name == "current_week"
            )
            .first()
        )

        if setting:

            try:

                return int(
                    setting.setting_value
                )

            except Exception:

                return 1

        active_week = (
            db.query(Week)
            .filter(
                Week.active == True
            )
            .first()
        )

        if active_week:

            return active_week.week_number

        return 1

    finally:

        db.close()