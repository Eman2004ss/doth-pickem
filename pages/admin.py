from datetime import datetime

from nicegui import ui
from services.export_service import (
    export_picks_to_excel
)
from services.week_service import (
    create_week,
    get_all_weeks
)

from services.team_service import (
    create_team,
    update_team,
    get_team_by_id
)

from services.game_service import (
    create_game,
    get_games_by_week
)

from services.espn_service import (
    find_event_by_teams
)

from services.logo_service import (
    download_logo
)

from services.rules_service import (
    save_rules_workbook_from_upload
)

from utils.constants import (
    VALID_TIERS,
    GAMES_PER_WEEK
)

from utils.ui_helpers import (
    dark_page_container
)


def admin_page():

    with dark_page_container():

        ui.label(
            "Admin Panel"
        ).classes(
            "text-h3"
        ).style(
            "color: white;"
        )

        ui.label(
            "Create Weekly Matchups"
        ).classes(
            "text-h5"
        ).style(
            "color: white;"
        )

        ui.label(
            "Use the exact ESPN team names, such as Louisville Cardinals, Ole Miss Rebels, Kansas City Chiefs, or Buffalo Bills."
        ).style(
            "color: #d1d5db;"
        )

        week_number = ui.number(
            label="Week Number",
            value=1,
            precision=0
        )

        game_inputs = []

        games_container = ui.column().classes(
            "w-full"
        )


        def add_game_input(game_number):

            with games_container:

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
                    """
                ):

                    ui.label(
                        f"Game {game_number}"
                    ).classes(
                        "text-h6"
                    ).style(
                        "color: white;"
                    )

                    sport = ui.select(
                        options=[
                            "ncaa",
                            "nfl"
                        ],
                        value="ncaa",
                        label="Sport"
                    )

                    away_team = ui.input(
                        label="Away Team"
                    )

                    home_team = ui.input(
                        label="Home Team"
                    )

                    tier = ui.select(
                        options=VALID_TIERS,
                        value="A",
                        label="Tier"
                    )

                    result_label = ui.label(
                        ""
                    ).style(
                        "color: #d1d5db;"
                    )

                    game_inputs.append(
                        {
                            "game_number": game_number,
                            "sport": sport,
                            "away_team": away_team,
                            "home_team": home_team,
                            "tier": tier,
                            "result_label": result_label
                        }
                    )


        for game_number in range(
            1,
            GAMES_PER_WEEK + 1
        ):
            add_game_input(
                game_number
            )


        def add_extra_game():

            add_game_input(
                len(game_inputs) + 1
            )


        ui.button(
            "+ Add Another Game",
            on_click=add_extra_game
        ).style(
            """
            background-color: #2563eb;
            color: white;
            font-weight: bold;
            margin-top: 12px;
            """
        )


        weeks_container = ui.column().classes(
            "w-full"
        )

        def load_weeks():

            weeks_container.clear()

            with weeks_container:

                ui.label(
                    "Existing Weeks"
                ).classes(
                    "text-h5"
                ).style(
                    "color: white; margin-top: 18px;"
                )

                weeks = get_all_weeks()

                if not weeks:

                    ui.label(
                        "No weeks created yet."
                    ).style(
                        "color: white;"
                    )

                    return

                for week in weeks:

                    games = get_games_by_week(
                        week.id
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
                        """
                    ):

                        ui.label(
                            f"Week {week.week_number}"
                        ).classes(
                            "text-h6"
                        ).style(
                            "color: white;"
                        )

                        ui.label(
                            f"{len(games)} Games"
                        ).style(
                            "color: #d1d5db;"
                        )

                        if not games:

                            ui.label(
                                "No games entered for this week."
                            ).style(
                                "color: #facc15;"
                            )

                        for game in games:

                            away_team = get_team_by_id(
                                game.away_team_id
                            )

                            home_team = get_team_by_id(
                                game.home_team_id
                            )

                            away_name = (
                                away_team.team_name
                                if away_team
                                else "Unknown Away Team"
                            )

                            home_name = (
                                home_team.team_name
                                if home_team
                                else "Unknown Home Team"
                            )

                            sport_label = (
                                game.sport.upper()
                                if game.sport
                                else "NCAA"
                            )

                            status = (
                                "ESPN linked"
                                if game.espn_event_id
                                else "No ESPN match"
                            )

                            status_color = (
                                "#22c55e"
                                if game.espn_event_id
                                else "#facc15"
                            )

                            with ui.row().classes(
                                "w-full items-center"
                            ).style(
                                """
                                background-color: #202020;
                                border: 1px solid #3a3a3a;
                                border-radius: 10px;
                                padding: 10px;
                                margin-top: 8px;
                                """
                            ):

                                ui.label(
                                    f"Game {game.game_number}: {away_name} vs {home_name}"
                                ).style(
                                    """
                                    color: white;
                                    font-weight: bold;
                                    width: 420px;
                                    """
                                )

                                ui.label(
                                    sport_label
                                ).style(
                                    """
                                    color: #60a5fa;
                                    font-weight: bold;
                                    width: 80px;
                                    """
                                )

                                ui.label(
                                    f"{game.tier} Tier"
                                ).style(
                                    """
                                    color: #d1d5db;
                                    width: 90px;
                                    """
                                )

                                ui.label(
                                    status
                                ).style(
                                    f"""
                                    color: {status_color};
                                    font-weight: bold;
                                    """
                                )

        def save_week():

            selected_week_number = int(
                week_number.value
            )

            week = create_week(
                selected_week_number
            )

            if not week:

                week = next(
                    (
                        existing_week
                        for existing_week in get_all_weeks()
                        if existing_week.week_number == selected_week_number
                    ),
                    None
                )

            if not week:

                ui.notify(
                    "Unable to create or find week.",
                    color="negative"
                )

                return

            created_games = 0
            matched_games = 0
            unmatched_games = 0

            for game_data in game_inputs:

                result_label = game_data[
                    "result_label"
                ]

                result_label.set_text(
                    ""
                )

                selected_sport = (
                    game_data["sport"].value
                    or "ncaa"
                )

                away_name = (
                    game_data["away_team"].value
                    or ""
                ).strip()

                home_name = (
                    game_data["home_team"].value
                    or ""
                ).strip()

                if not away_name or not home_name:

                    continue

                away_team = create_team(
                    team_name=away_name,
                    sport=selected_sport
                )

                home_team = create_team(
                    team_name=home_name,
                    sport=selected_sport
                )

                if not away_team or not home_team:

                    result_label.set_text(
                        "Unable to create one or both teams."
                    )

                    result_label.style(
                        "color: #ef4444;"
                    )

                    unmatched_games += 1

                    continue

                event = find_event_by_teams(
                    away_team_name=away_name,
                    home_team_name=home_name,
                    sport=selected_sport
                )

                espn_event_id = None
                kickoff_time = None

                if event:

                    matched_games += 1

                    espn_event_id = event.get(
                        "event_id"
                    )

                    kickoff_raw = event.get(
                        "kickoff"
                    )

                    if kickoff_raw:

                        try:

                            kickoff_time = datetime.fromisoformat(
                                kickoff_raw.replace(
                                    "Z",
                                    "+00:00"
                                )
                            )

                        except Exception:

                            kickoff_time = None

                    away_espn_data = event.get(
                        "away_team",
                        {}
                    )

                    home_espn_data = event.get(
                        "home_team",
                        {}
                    )

                    away_logo_path = None
                    home_logo_path = None

                    away_logo_url = away_espn_data.get(
                        "logo"
                    )

                    home_logo_url = home_espn_data.get(
                        "logo"
                    )

                    if away_logo_url:

                        away_logo_path = download_logo(
                            away_logo_url,
                            away_name
                        )

                    if home_logo_url:

                        home_logo_path = download_logo(
                            home_logo_url,
                            home_name
                        )

                    update_team(
                        away_team.id,
                        espn_team_id=away_espn_data.get(
                            "espn_team_id"
                        ),
                        abbreviation=away_espn_data.get(
                            "abbreviation"
                        ),
                        record=away_espn_data.get(
                            "record"
                        ),
                        logo_path=away_logo_path or away_logo_url,
                        sport=selected_sport
                    )

                    update_team(
                        home_team.id,
                        espn_team_id=home_espn_data.get(
                            "espn_team_id"
                        ),
                        abbreviation=home_espn_data.get(
                            "abbreviation"
                        ),
                        record=home_espn_data.get(
                            "record"
                        ),
                        logo_path=home_logo_path or home_logo_url,
                        sport=selected_sport
                    )

                    result_label.set_text(
                        f"ESPN match found. Event ID: {espn_event_id}"
                    )

                    result_label.style(
                        "color: #22c55e;"
                    )

                else:

                    unmatched_games += 1

                    result_label.set_text(
                        "No ESPN match found. Check exact team names and sport."
                    )

                    result_label.style(
                        "color: #facc15;"
                    )

                game = create_game(
                    week_id=week.id,
                    game_number=game_data[
                        "game_number"
                    ],
                    tier=game_data[
                        "tier"
                    ].value,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_time=kickoff_time,
                    espn_event_id=espn_event_id,
                    sport=selected_sport
                )

                if game:

                    created_games += 1

            ui.notify(
                f"{created_games} games saved. {matched_games} ESPN matches, {unmatched_games} unmatched.",
                color="positive"
            )

            load_weeks()

        ui.button(
            "Save Week",
            on_click=save_week
        ).style(
            """
            background-color: #22c55e;
            color: white;
            font-weight: bold;
            margin-top: 14px;
            """
        )

        ui.separator().style(
            "background-color: #333333; margin-top: 18px;"
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
            margin-top: 18px;
            """
        ):

            ui.label(
                "Upload Updated Rules Workbook"
            ).classes(
                "text-h5"
            ).style(
                "color: white;"
            )

            ui.label(
                "Upload the updated Excel workbook. The Rules page will read the Master Plan - Football Season sheet."
            ).style(
                "color: #d1d5db;"
            )

            upload_status = ui.label(
                ""
            ).style(
                "color: #d1d5db;"
            )

            def handle_rules_upload(upload_event):

                success = save_rules_workbook_from_upload(
                    upload_event
                )

                if success:

                    upload_status.set_text(
                        "Rules workbook uploaded successfully."
                    )

                    upload_status.style(
                        "color: #22c55e;"
                    )

                    ui.notify(
                        "Rules workbook uploaded.",
                        color="positive"
                    )

                else:

                    upload_status.set_text(
                        "Upload failed. Make sure the file is a valid .xlsx workbook."
                    )

                    upload_status.style(
                        "color: #ef4444;"
                    )

                    ui.notify(
                        "Rules workbook upload failed.",
                        color="negative"
                    )

            ui.upload(
                label="Upload Rules Workbook",
                on_upload=handle_rules_upload,
                auto_upload=True
            ).props(
                "accept=.xlsx"
            ).classes(
                "w-full"
            )

        ui.separator().style(
            "background-color: #333333; margin-top: 18px;"
        )
    
        def export_excel():

            success = export_picks_to_excel()

            if success:

                ui.notify(
                    "Excel export created.",
                    color="positive"
                )

            else:

                ui.notify(
                    "Excel export failed.",
                    color="negative"
                )

        ui.button(
                "Export Picks to Excel",
                on_click=export_excel
            ).style(
                """
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                margin-top: 12px;
                """
            )
        load_weeks()