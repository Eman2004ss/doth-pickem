from nicegui import ui

from services.week_service import (
    get_all_weeks
)

from services.game_service import (
    get_games_by_week
)

from services.team_service import (
    get_team_by_id
)

from utils.ui_helpers import (
    dark_page_container
)


def live_results_page():

    with dark_page_container():

        ui.label(
            "Live Results"
        ).classes(
            "text-h3"
        ).style(
            "color: white;"
        )

        weeks = get_all_weeks()

        week_options = {
            f"Week {week.week_number}": week.id
            for week in weeks
        }

        week_select = ui.select(
            options=list(
                week_options.keys()
            ),
            label="Select Week"
        )

        results_container = ui.column().classes(
            "w-full"
        )

        def logo_source(team):

            if not team:
                return None

            if not team.logo_path:
                return None

            if (
                team.logo_path.startswith("http://")
                or
                team.logo_path.startswith("https://")
            ):

                return team.logo_path

            if team.logo_path.startswith(
                "/assets/"
            ):

                return team.logo_path

            if team.logo_path.startswith(
                "assets/"
            ):

                return "/" + team.logo_path

            return team.logo_path

        def team_score_row(
            team,
            score
        ):

            with ui.row().classes(
                "w-full items-center justify-between no-wrap"
            ).style(
                """
                background-color: #202020;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 14px;
                margin-top: 8px;
                overflow: visible;
                gap: 20px;
                box-sizing: border-box;
                """
            ):

                with ui.row().classes(
                    "items-center no-wrap"
                ).style(
                    """
                    gap: 20px;
                    overflow: visible;
                    min-width: 0;
                    flex: 1;
                    """
                ):

                    logo = logo_source(
                        team
                    )
                    if logo:

                        with ui.element('div').style("""
                            width: 160px;
                            height: 160px;
                            flex-shrink: 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        """):

                            ui.image(
                                logo
                            ).style(
                                """
                                max-width: 100%;
                                max-height: 100%;
                                object-fit: contain;
                                object-position: center;
                                background-color: transparent;
                                """
                            )

                    with ui.column().style(
                        """
                        min-width: 0;
                        overflow: visible;
                        flex: 1;
                        """
                    ):

                        ui.label(
                            team.team_name
                        ).style(
                            """
                            color: white;
                            font-weight: bold;
                            font-size: 18px;
                            white-space: normal;
                            overflow-wrap: break-word;
                            line-height: 1.2;
                            """
                        )

                        ui.label(
                            team.record
                            or "Record Unavailable"
                        ).style(
                            "color: #d1d5db;"
                        )

                ui.label(
                    str(score)
                ).classes(
                    "text-h4"
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 110px;
                    min-width: 110px;
                    text-align: right;
                    padding-right: 12px;
                    box-sizing: border-box;
                    flex-shrink: 0;
                    """
                )

        def load_games():

            results_container.clear()

            if not week_select.value:
                return

            week_id = week_options[
                week_select.value
            ]

            games = get_games_by_week(
                week_id
            )

            with results_container:

                if not games:

                    ui.label(
                        "No games created for this week."
                    ).style(
                        "color: white;"
                    )

                    return

                for game in games:

                    home_team = get_team_by_id(
                        game.home_team_id
                    )

                    away_team = get_team_by_id(
                        game.away_team_id
                    )

                    if not home_team or not away_team:
                        continue

                    with ui.card().classes(
                        "w-full"
                    ).style(
                        """
                        background-color: #151515;
                        color: white;
                        border: 1px solid #333333;
                        border-radius: 14px;
                        padding: 18px;
                        overflow: visible;
                        box-sizing: border-box;
                        """
                    ):

                        ui.label(
                            f"{away_team.team_name} vs {home_team.team_name}"
                        ).classes(
                            "text-h5"
                        ).style(
                            """
                            color: white;
                            white-space: normal;
                            overflow-wrap: break-word;
                            """
                        )

                        ui.label(
                            f"{game.tier} Tier"
                        ).style(
                            "color: #d1d5db;"
                        )

                        team_score_row(
                            away_team,
                            game.away_score
                        )

                        team_score_row(
                            home_team,
                            game.home_score
                        )

                        ui.separator().style(
                            "background-color: #333333;"
                        )

                        ui.label(
                            f"Status: {game.game_status}"
                        ).style(
                            "color: white; font-weight: bold;"
                        )

                        if game.game_clock:

                            ui.label(
                                game.game_clock
                            ).style(
                                "color: #d1d5db;"
                            )

                        if game.completed:

                            ui.label(
                                "Final"
                            ).style(
                                "color: #22c55e; font-weight: bold;"
                            )

        week_select.on(
            "update:model-value",
            lambda e: load_games()
        )

        if week_options:

            first_week = list(
                week_options.keys()
            )[0]

            week_select.set_value(
                first_week
            )

            load_games()

        ui.timer(
            60,
            load_games
        )