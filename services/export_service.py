import pandas as pd

from database.db import SessionLocal

from database.models import (
    User,
    Week,
    Game,
    Team,
    Pick
)


def export_picks_to_excel():

    session = SessionLocal()

    try:

        rows = []

        weeks = session.query(
            Week
        ).all()

        for week in weeks:

            games = session.query(
                Game
            ).filter(
                Game.week_id == week.id
            ).all()

            for user in session.query(
                User
            ).all():

                row = {
                    "Week": week.week_number,
                    "Name": user.username
                }

                games = sorted(
                    games,
                    key=lambda x: x.game_number
                )

                for game in games:

                    pick = session.query(
                        Pick
                    ).filter(
                        Pick.user_id == user.id,
                        Pick.game_id == game.id
                    ).first()

                    game_number = game.game_number

                    row[
                        f"Game {game_number} Tier"
                    ] = game.tier

                    if pick:

                        team = session.query(
                            Team
                        ).filter(
                            Team.id == pick.selected_team_id
                        ).first()

                        row[
                            f"Game {game_number} Pick"
                        ] = (
                            team.team_name
                            if team
                            else ""
                        )

                    else:

                        row[
                            f"Game {game_number} Pick"
                        ] = ""

                rows.append(
                    row
                )

        pd.DataFrame(
            rows
        ).to_excel(
            "picks_export.xlsx",
            index=False
        )

        return True

    except Exception as ex:

        print(
            f"Export Error: {ex}"
        )

        return False

    finally:

        session.close()