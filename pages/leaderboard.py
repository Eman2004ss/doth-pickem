from nicegui import ui

from services.leaderboard_service import (
    get_leaderboard
)

from services.user_service import (
    get_user_by_id
)

from utils.ui_helpers import (
    dark_page_container
)


def leaderboard_page():

    with dark_page_container():

        ui.label(
            "Leaderboard"
        ).style(
            """
            color: white;
            font-size: clamp(32px, 8vw, 56px);
            font-weight: bold;
            """
        )

        leaderboard_rows = get_leaderboard()

        if not leaderboard_rows:

            ui.label(
                "No leaderboard data available."
            ).style(
                "color: white;"
            )

            return

        for row in leaderboard_rows:

            user = get_user_by_id(
                row.user_id
            )

            if not user:
                continue

            accuracy = 0

            if row.total_picks > 0:

                accuracy = round(
                    (
                        row.correct_picks
                        / row.total_picks
                    ) * 100,
                    1
                )

            rank_color = "#ffffff"
            border_color = "#333333"
            medal = ""

            if row.rank == 1:

                medal = "🥇"
                rank_color = "gold"
                border_color = "gold"

            elif row.rank == 2:

                medal = "🥈"
                rank_color = "silver"
                border_color = "silver"

            elif row.rank == 3:

                medal = "🥉"
                rank_color = "#cd7f32"
                border_color = "#cd7f32"

            with ui.card().classes(
                "w-full"
            ).style(
                f"""
                background-color: #151515;
                color: white;
                border: 1px solid {border_color};
                border-left: 8px solid {border_color};
                border-radius: 16px;
                padding: 20px;
                margin-top: 12px;
                """
            ):

                ui.label(
                    f"{medal} {user.username}"
                ).style(
                    """
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    """
                )

                ui.separator().style(
                    "background-color: #333333;"
                )

                with ui.grid(
                    columns=2
                ).classes(
                    "w-full"
                ).style(
                    "margin-top: 10px;"
                ):

                    with ui.column():

                        ui.label(
                            "Points"
                        ).style(
                            "color: #9ca3af;"
                        )

                        ui.label(
                            str(
                                row.total_points
                            )
                        ).style(
                            """
                            color: #22c55e;
                            font-size: 28px;
                            font-weight: bold;
                            """
                        )

                    with ui.column():

                        ui.label(
                            "Accuracy"
                        ).style(
                            "color: #9ca3af;"
                        )

                        ui.label(
                            f"{accuracy}%"
                        ).style(
                            """
                            color: white;
                            font-size: 28px;
                            font-weight: bold;
                            """
                        )

                    with ui.column():

                        ui.label(
                            "Weekly Wins"
                        ).style(
                            "color: #9ca3af;"
                        )

                        ui.label(
                            str(
                                row.weekly_wins
                            )
                        ).style(
                            """
                            color: #60a5fa;
                            font-size: 28px;
                            font-weight: bold;
                            """
                        )

                    with ui.column():

                        ui.label(
                            "Correct Picks"
                        ).style(
                            "color: #9ca3af;"
                        )

                        ui.label(
                            str(
                                row.correct_picks
                            )
                        ).style(
                            """
                            color: white;
                            font-size: 28px;
                            font-weight: bold;
                            """
                        )

                ui.separator().style(
                    """
                    background-color: #333333;
                    margin-top: 10px;
                    margin-bottom: 10px;
                    """
                )

                with ui.row().classes(
                    "justify-around w-full"
                ):

                    ui.label(
                        f"📋 Total Picks: {row.total_picks}"
                    ).style(
                        "color: #d1d5db;"
                    )