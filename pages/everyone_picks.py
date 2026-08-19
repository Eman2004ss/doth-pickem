from nicegui import ui
from services.logo_service import get_local_logo_path
from services.week_service import (
    get_all_weeks
)

from services.game_service import (
    get_games_by_week
)

from services.pick_service import (
    get_game_picks
)

from services.locking_service import (
    is_game_locked
)

from services.team_service import (
    get_team_by_id
)

from services.user_service import (
    get_user_by_id
)

from utils.helpers import (
    format_kickoff_et
)

from utils.ui_helpers import (
    dark_page_container
)


def everyone_picks_page():

    with dark_page_container():

        ui.label(
            "Everyone's Picks"
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

        content = ui.column().classes(
            "w-full"
        )

        def logo_source(team):
            if not team:
                return None
            return "/" + get_local_logo_path(team.team_name)"       
        
        def team_block(team):

            with ui.column().style(
                """
                width: 100%;
                min-width: 0;
                align-items: center;
                text-align: center;
                overflow: hidden;
                """
            ):

                logo = logo_source(
                    team
                )

                if logo:
                
                    with ui.element('div').style("""
                        width: min(160px, 25vw);
                        height: min(160px,25vw);
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

                ui.label(
                    team.team_name
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    max-width: 100%;
                    white-space: normal;
                    overflow-wrap: break-word;
                    word-break: normal;
                    text-align: center;
                    line-height: 1.2;
                    margin-top: 6px;
                    """
                )

        def team_header(
            away_team,
            home_team,
            game
        ):

            with ui.element("div").style(
                """
                display: grid;
                grid-template-columns: minmax(0, 1fr) 70px minmax(0, 1fr);
                align-items: center;
                gap: 16px;
                width: 100%;
                overflow: hidden;
                """
            ):

                team_block(
                    away_team
                )

                ui.label(
                    "vs"
                ).style(
                    """
                    color: #d1d5db;
                    font-weight: bold;
                    font-size: 18px;
                    text-align: center;
                    width: 70px;
                    """
                )

                team_block(
                    home_team
                )

            ui.label(
                f"Game {game.game_number} • {game.tier} Tier"
            ).style(
                "color: #d1d5db; margin-top: 12px;"
            )

        def pick_row(pick):

            user = get_user_by_id(
                pick.user_id
            )

            selected_team = get_team_by_id(
                pick.selected_team_id
            )

            if not user or not selected_team:
                return

            row_style = """
            background-color: #202020;
            color: white;
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 10px;
            margin-top: 8px;
            """

            result_text = ""
            result_color = "#d1d5db"

            if pick.is_correct is True:

                row_style = """
                background-color: rgba(34, 197, 94, 0.18);
                color: white;
                border: 1px solid #22c55e;
                border-radius: 10px;
                padding: 10px;
                margin-top: 8px;
                """

                result_text = "Correct"
                result_color = "#22c55e"

            elif pick.is_correct is False:

                row_style = """
                background-color: rgba(239, 68, 68, 0.18);
                color: white;
                border: 1px solid #ef4444;
                border-radius: 10px;
                padding: 10px;
                margin-top: 8px;
                """

                result_text = "Incorrect"
                result_color = "#ef4444"

            with ui.row().classes(
                "w-full items-center justify-between wrap"
            ).style(
                row_style
            ):

                ui.label(
                    user.username
                ).style(
                    """
                    color: white;
                    font-weight: bold;
                    width: 150px;
                    """
                )

                ui.label(
                    selected_team.team_name
                ).style(
                    """
                    color: white;
                    flex: 1;
                    """
                )

                if result_text:

                    ui.label(
                        result_text
                    ).style(
                        f"""
                        color: {result_color};
                        font-weight: bold;
                        """
                    )

        def load_games():

            content.clear()

            if not week_select.value:
                return

            week_id = week_options[
                week_select.value
            ]

            games = get_games_by_week(
                week_id
            )

            with content:

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

                    locked = is_game_locked(
                        game.id
                    )

                    with ui.card().classes(
                        "w-full"
                    ).style(
                        """
                        background-color: #151515;
                        color: white;
                        border: 1px solid #333333;
                        border-radius: 14px;
                        padding: 18px;
                        margin-top: 12px;
                        overflow: hidden;
                        """
                    ):

                        team_header(
                            away_team,
                            home_team,
                            game
                        )

                        ui.separator().style(
                            "background-color: #333333; margin-top: 14px;"
                        )

                        if not locked:

                            ui.label(
                                "GAME NOT LOCKED YET"
                            ).style(
                                """
                                color: #facc15;
                                font-weight: bold;
                                font-size: 16px;
                                margin-top: 8px;
                                """
                            )

                            ui.label(
                                "Everyone's picks will be shown once this game starts."
                            ).style(
                                "color: #d1d5db;"
                            )

                            ui.label(
                                f"Kickoff: {format_kickoff_et(game.kickoff_time)}"
                            ).style(
                                "color: #d1d5db;"
                            )

                            continue

                        ui.label(
                            "PICKS ARE LOCKED"
                        ).style(
                            """
                            color: #22c55e;
                            font-weight: bold;
                            font-size: 16px;
                            margin-top: 8px;
                            """
                        )

                        picks = get_game_picks(
                            game.id
                        )

                        if not picks:

                            ui.label(
                                "No picks submitted."
                            ).style(
                                "color: white;"
                            )

                            continue

                        for pick in picks:

                            pick_row(
                                pick
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