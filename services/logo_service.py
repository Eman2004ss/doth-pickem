import os
import re
import requests

from database.db import SessionLocal
from database.models import Team


LOGO_FOLDER = "assets/logos"
DEFAULT_LOGO = "assets/logos/default.png"


def ensure_logo_folder():

    os.makedirs(
        LOGO_FOLDER,
        exist_ok=True
    )


def clean_filename(team_name):

    name = team_name.lower()

    name = name.replace(
        "&",
        "and"
    )

    name = name.replace(
        "'",
        ""
    )

    name = name.replace(
        ".",
        ""
    )

    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        name
    )

    name = name.strip("_")

    return f"{name}.png"


def get_local_logo_path(team_name):

    ensure_logo_folder()

    filename = clean_filename(
        team_name
    )

    return os.path.join(
        LOGO_FOLDER,
        filename
    )


def find_local_logo_for_team(team_name):

    if not team_name:
        return None

    local_path = get_local_logo_path(
        team_name
    )

    if os.path.exists(
        local_path
    ):

        return local_path

    return None


def download_logo(
    logo_url,
    team_name
):

    if not logo_url:
        return None

    ensure_logo_folder()

    local_path = get_local_logo_path(
        team_name
    )

    if os.path.exists(
        local_path
    ):

        return local_path

    try:

        response = requests.get(
            logo_url,
            timeout=30
        )

        response.raise_for_status()

        with open(
            local_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        return local_path

    except Exception:

        return None


def save_logo_for_team(
    team_id,
    logo_url
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

        local_path = download_logo(
            logo_url,
            team.team_name
        )

        if not local_path:
            return False

        team.logo_path = local_path

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def get_logo_path(team_id):

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
            return DEFAULT_LOGO

        if not team.logo_path:

            local_logo = find_local_logo_for_team(
                team.team_name
            )

            if local_logo:

                team.logo_path = local_logo

                db.commit()

                return local_logo

            return DEFAULT_LOGO

        if (
            team.logo_path.startswith("http://")
            or
            team.logo_path.startswith("https://")
        ):

            return team.logo_path

        if os.path.exists(
            team.logo_path
        ):

            return team.logo_path

        local_logo = find_local_logo_for_team(
            team.team_name
        )

        if local_logo:

            team.logo_path = local_logo

            db.commit()

            return local_logo

        return DEFAULT_LOGO

    finally:

        db.close()


def set_logo_path(
    team_id,
    logo_path
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

        team.logo_path = logo_path

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def logo_exists(team_id):

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

        if not team.logo_path:
            return False

        if (
            team.logo_path.startswith("http://")
            or
            team.logo_path.startswith("https://")
        ):

            return True

        return os.path.exists(
            team.logo_path
        )

    finally:

        db.close()


def update_all_missing_logos():

    db = SessionLocal()

    try:

        teams = db.query(Team).all()

        updated_count = 0

        for team in teams:

            local_logo = find_local_logo_for_team(
                team.team_name
            )

            if local_logo:

                team.logo_path = local_logo

                updated_count += 1

        db.commit()

        return updated_count

    except Exception:

        db.rollback()

        return 0

    finally:

        db.close()

def get_logo_path_by_name(team_name):
    """Look up a logo the same way get_logo_path does, but by team name
    instead of team_id -- used by features (like the playoff bracket) that
    only store plain team-name strings rather than a foreign key."""

    if not team_name or team_name.strip().upper() == "TBD":
        return DEFAULT_LOGO

    db = SessionLocal()

    try:

        team = (
            db.query(Team)
            .filter(Team.team_name == team_name)
            .first()
        )

        if not team:
            local_logo = find_local_logo_for_team(team_name)
            return local_logo or DEFAULT_LOGO

        return get_logo_path(team.id)

    finally:

        db.close()
