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
        ).classes(
            "text-h3"
        ).style(
            "color: white;"
        )

        leaderboard_rows = get_leaderboard()

        if not leaderboard_rows:

            ui.label(
                "No leaderboard data available."
            ).style(
                "color: white;"
            )

            return

        with ui.card().classes(
            "w-full"
        ).style(
            """
            background-color: #151515;
            color: white;
            border: 1px solid #333333;
            border-radius: 14px;
            padding: 18px;
            """
        ):

            with ui.row().classes(
                "w-full items-center"
            ):

                ui.label(
                    "Rank"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 90px;
                    """
                )

                ui.label(
                    "Player"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 180px;
                    """
                )

                ui.label(
                    "Points"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 120px;
                    """
                )

                ui.label(
                    "Accuracy"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 120px;
                    """
                )

                ui.label(
                    "Weekly Wins"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 140px;
                    """
                )

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

            if row.rank == 1:

                rank_color = "gold"
                border_color = "gold"

            elif row.rank == 2:

                rank_color = "silver"
                border_color = "silver"

            elif row.rank == 3:

                rank_color = "#cd7f32"
                border_color = "#cd7f32"

            with ui.card().classes(
                "w-full"
            ).style(
                f"""
                background-color: #151515;
                color: white;
                border: 1px solid {border_color};
                border-left: 6px solid {border_color};
                border-radius: 14px;
                padding: 18px;
                """
            ):

                with ui.row().classes(
                    "w-full items-center"
                ):

                    ui.label(
                        f"#{row.rank}"
                    ).style(
                        f"""
                        color: {rank_color};
                        font-weight: bold;
                        font-size: 22px;
                        width: 90px;
                        """
                    )

                    ui.label(
                        user.username
                    ).style(
                        """
                        color: white;
                        font-weight: bold;
                        font-size: 18px;
                        width: 180px;
                        """
                    )

                    ui.label(
                        str(
                            row.total_points
                        )
                    ).style(
                        """
                        color: #22c55e;
                        font-weight: bold;
                        font-size: 18px;
                        width: 120px;
                        """
                    )

                    ui.label(
                        f"{accuracy}%"
                    ).style(
                        """
                        color: #d1d5db;
                        width: 120px;
                        """
                    )

                    ui.label(
                        str(
                            row.weekly_wins
                        )
                    ).style(
                        """
                        color: #60a5fa;
                        font-weight: bold;
                        width: 140px;
                        """
                    )

                ui.separator().style(
                    "background-color: #333333;"
                )

                with ui.row().classes(
                    "w-full"
                ):

                    ui.label(
                        f"Correct Picks: {row.correct_picks}"
                    ).style(
                        "color: #d1d5db;"
                    )

                    ui.label(
                        f"Total Picks: {row.total_picks}"
                    ).style(
                        "color: #d1d5db;"
                    )