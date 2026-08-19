from nicegui import ui, app

from services.week_service import (
    get_active_week
)

from services.game_service import (
    get_games_by_week
)

from services.team_service import (
    get_team_by_id
)

from services.leaderboard_service import (
    get_leaderboard
)

from services.user_service import (
    get_user_by_id
)

from utils.helpers import (
    format_kickoff_et
)
def home_page():

    ui.dark_mode().enable()

    with ui.column().style(
        """
        background-color: #050505;
        color: white;
        min-height: 100vh;
        width: 100%;
        padding: 20px;
        box-sizing: border-box;
        """
    ).classes(
        "w-full"
    ):

        username = app.storage.user.get(
            "username",
            "Guest"
        )

        is_admin = app.storage.user.get(
            "is_admin",
            False
        )

        with ui.row().classes(
            "w-full items-center justify-between"
        ):

            ui.label(
                f"Welcome, {username}"
            ).classes(
                "text-h3"
            ).style(
                "color: white;"
            )

            def logout():

                app.storage.user.clear()

                ui.notify(
                    "Logged out.",
                    color="positive"
                )

                ui.navigate.to(
                    "/"
                )

            ui.button(
                "Logout",
                icon="logout",
                on_click=logout
            ).style(
                """
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 8px 14px;
                """
            )

        with ui.row().classes(
            "items-center"
        ):

            ui.button(
                "Weekly Picks",
                on_click=lambda:
                ui.navigate.to(
                    "/weekly-picks"
                )
            )

            ui.button(
                "Everyone's Picks",
                on_click=lambda:
                ui.navigate.to(
                    "/everyone-picks"
                )
            )

            ui.button(
                "Live Results",
                on_click=lambda:
                ui.navigate.to(
                    "/live-results"
                )
            )

            ui.button(
                "Leaderboard",
                on_click=lambda:
                ui.navigate.to(
                    "/leaderboard"
                )
            )

            ui.button(
                "Rules",
                on_click=lambda:
                ui.navigate.to(
                    "/rules"
                )
            )

            if is_admin:

                ui.button(
                    "Admin",
                    on_click=lambda:
                    ui.navigate.to(
                        "/admin"
                    )
                )

        ui.separator().style(
            "background-color: #333333;"
        )

        active_week = get_active_week()

        with ui.card().classes(
            "w-full"
        ).style(
            """
            background-color: #151515;
            color: white;
            border: 1px solid #333333;
            border-radius: 14px;
            """
        ):

            ui.label(
                "Current Week"
            ).classes(
                "text-h5"
            ).style(
                "color: white;"
            )

            if active_week:

                ui.label(
                    f"Week {active_week.week_number}"
                ).style(
                    "color: white;"
                )

            else:

                ui.label(
                    "No Active Week"
                ).style(
                    "color: white;"
                )

        with ui.card().classes(
            "w-full"
        ).style(
            """
            background-color: #151515;
            color: white;
            border: 1px solid #333333;
            border-radius: 14px;
            """
        ):

            ui.label(
                "Top Standings"
            ).classes(
                "text-h5"
            ).style(
                "color: white;"
            )

            leaderboard = get_leaderboard()

            if leaderboard:

                for row in leaderboard:

                    user = get_user_by_id(
                        row.user_id
                    )

                    if not user:
                        continue

                    ui.label(
                        f"#{row.rank} {user.username} ({row.total_points} pts)"
                    ).style(
                        "color: white;"
                    )

            else:

                ui.label(
                    "No standings available."
                ).style(
                    "color: white;"
                )

        with ui.card().classes(
            "w-full"
        ).style(
            """
            background-color: #151515;
            color: white;
            border: 1px solid #333333;
            border-radius: 14px;
            """
        ):

            ui.label(
                "Upcoming Games"
            ).classes(
                "text-h5"
            ).style(
                "color: white;"
            )

            if not active_week:

                ui.label(
                    "No games available."
                ).style(
                    "color: white;"
                )

            else:

                games = get_games_by_week(
                    active_week.id
                )

                if not games:

                    ui.label(
                        "No games created."
                    ).style(
                        "color: white;"
                    )

                for game in games:

                    away_team = get_team_by_id(
                        game.away_team_id
                    )

                    home_team = get_team_by_id(
                        game.home_team_id
                    )

                    if not away_team or not home_team:
                        continue

                    with ui.card().style(
                        """
                        background-color: #202020;
                        color: white;
                        border: 1px solid #3a3a3a;
                        border-radius: 12px;
                        padding: 16px;
                        """
                    ):

                        ui.label(
                            f"{away_team.team_name} vs {home_team.team_name}"
                        ).style(
                            "color: white; font-weight: bold;"
                        )

                        ui.label(
                            f"{game.tier} Tier"
                        ).style(
                            "color: white;"
                        )

                        if game.kickoff_time:

                            ui.label(
                                f"Kickoff: {format_kickoff_et(game.kickoff_time)}"
                            ).style(
                                "color: #d1d5db;"
                            )