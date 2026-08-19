from database.db import SessionLocal

from database.models import Team

from services.logo_service import (
    find_local_logo_for_team
)

def create_team(
    team_name,
    espn_team_id=None,
    abbreviation=None,
    conference=None,
    sport=None,
    logo_path=None,
    primary_color=None,
    secondary_color=None,
    record=None
):

    db = SessionLocal()

    try:

        existing_team = (
            db.query(Team)
            .filter(
                Team.team_name == team_name
            )
            .first()
        )
        if existing_team:

            local_logo = find_local_logo_for_team(
                team_name
            )

            if local_logo:

                existing_team.logo_path = local_logo

                db.commit()

                db.refresh(
                    existing_team
                )

            return existing_team

        if not logo_path:

            local_logo = find_local_logo_for_team(
                team_name
            )

            if local_logo:

                logo_path = local_logo
                        
        team = Team(
            team_name=team_name,
            espn_team_id=espn_team_id,
            abbreviation=abbreviation,
            conference=conference,
            sport=sport,
            logo_path=logo_path,
            primary_color=primary_color,
            secondary_color=secondary_color,
            record=record
        )

        db.add(team)

        db.commit()

        db.refresh(team)

        return team

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


def get_team_by_id(team_id):

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    finally:

        db.close()


def get_team_by_name(team_name):

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .filter(
                Team.team_name == team_name
            )
            .first()
        )

    finally:

        db.close()


def get_team_by_espn_id(
    espn_team_id
):

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .filter(
                Team.espn_team_id == str(
                    espn_team_id
                )
            )
            .first()
        )

    finally:

        db.close()


def get_all_teams():

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .order_by(
                Team.team_name
            )
            .all()
        )

    finally:

        db.close()


def search_teams(search_text):

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .filter(
                Team.team_name.ilike(
                    f"%{search_text}%"
                )
            )
            .order_by(
                Team.team_name
            )
            .all()
        )

    finally:

        db.close()


def update_team(
    team_id,
    **kwargs
):

    db = SessionLocal()

    try:

        team = (
            db.query(Team)
            .filter(
                Team.id == team_id
            )
            .first()
        )

        if not team:
            return False

        for key, value in kwargs.items():

            if hasattr(team, key):
                setattr(
                    team,
                    key,
                    value
                )

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_record(
    team_id,
    record
):

    db = SessionLocal()

    try:

        team = (
            db.query(Team)
            .filter(
                Team.id == team_id
            )
            .first()
        )

        if not team:
            return False

        team.record = record

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def delete_team(team_id):

    db = SessionLocal()

    try:

        team = (
            db.query(Team)
            .filter(
                Team.id == team_id
            )
            .first()
        )

        if not team:
            return False

        db.delete(team)

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def team_exists(team_name):

    db = SessionLocal()

    try:

        return (
            db.query(Team)
            .filter(
                Team.team_name == team_name
            )
            .first()
        ) is not None

    finally:

        db.close()