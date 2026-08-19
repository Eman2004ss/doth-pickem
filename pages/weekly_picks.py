from nicegui import ui, app

from services.week_service import (
    get_all_weeks
)

from services.game_service import (
    get_games_by_week
)

from services.pick_service import (
    create_pick,
    update_pick,
    get_user_pick
)

from services.team_service import (
    get_team_by_id
)

from services.locking_service import (
    is_game_locked
)

from utils.ui_helpers import (
    dark_page_container
)


def weekly_picks_page():

    with dark_page_container():

        ui.label(
            "Weekly Picks"
        ).classes(
            "text-h3"
        ).style(
            "color: white;"
        )

        user_id = app.storage.user.get(
            "user_id"
        )

        if not user_id:

            ui.label(
                "Please log in first."
            ).style(
                "color: white;"
            )

            ui.button(
                "Go To Login",
                on_click=lambda: ui.navigate.to("/")
            )

            return

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
        ).style(
            "color: white;"
        )

        content = ui.column().classes(
            "w-full"
        )

        def logo_source(team):

            if not team:
                return None

            if not team.logo_path:
                return None

            if team.logo_path.startswith(
                "http://"
            ) or team.logo_path.startswith(
                "https://"
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

        def save_pick(
            game_id,
            team_id
        ):

            existing_pick = get_user_pick(
                user_id,
                game_id
            )

            if existing_pick:

                success = update_pick(
                    user_id,
                    game_id,
                    team_id
                )

                if success:

                    ui.notify(
                        "Pick Updated",
                        color="positive"
                    )

                else:

                    ui.notify(
                        "Game Locked",
                        color="negative"
                    )

            else:

                create_pick(
                    user_id,
                    game_id,
                    team_id
                )

                ui.notify(
                    "Pick Saved",
                    color="positive"
                )

            load_games()

        def team_pick_card(
            team,
            button_text,
            game,
            locked
        ):

            with ui.card().style(
                """
                background-color: #202020;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 14px;
                padding: 16px;
                min-width: 420px;
                overflow: visible;
                """
            ):

                with ui.row().classes(
                    "items-center no-wrap"
                ).style(
                    """
                    gap: 20px;
                    overflow: visible;
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

                    with ui.column().style(
                        """
                        min-width: 220px;
                        """
                    ):

                        ui.label(
                            team.team_name
                        ).style(
                            "color: white; font-weight: bold; font-size: 18px;"
                        )

                        ui.label(
                            team.record
                            or "Record Unavailable"
                        ).style(
                            """
                            color: #d1d5db;
                            white-space: nowrap;
                            """
                        )

                        pick_button = ui.button(
                            button_text,
                            on_click=lambda:
                            save_pick(
                                game.id,
                                team.id
                            )
                        )

                        if locked:

                            pick_button.disable()

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

                    current_pick = get_user_pick(
                        user_id,
                        game.id
                    )

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
                        """
                    ):

                        ui.label(
                            f"{away_team.team_name} vs {home_team.team_name}"
                        ).classes(
                            "text-h5"
                        ).style(
                            "color: white;"
                        )

                        ui.label(
                            f"{game.tier} Tier"
                        ).style(
                            "color: #d1d5db;"
                        )

                        if locked:

                            ui.label(
                                "LOCKED"
                            ).style(
                                "color: #ef4444; font-weight: bold;"
                            )

                        with ui.row().classes(
                            "w-full items-center justify-between wrap"
                        ):

                            team_pick_card(
                                away_team,
                                "Pick Away Team",
                                game,
                                locked
                            )

                            team_pick_card(
                                home_team,
                                "Pick Home Team",
                                game,
                                locked
                            )

                        if current_pick:

                            selected_team = get_team_by_id(
                                current_pick.selected_team_id
                            )

                            if selected_team:

                                ui.label(
                                    f"Your Pick: {selected_team.team_name}"
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