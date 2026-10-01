from datetime import datetime
from utils.team_data import (
    NCAA_CONFERENCES,
    NFL_DIVISIONS,
    NHL_DIVISIONS,
)
from nicegui import app, ui
from services.admin_game_service import remove_game_as_admin, update_game_tier_as_admin
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

from utils.constants import (
    VALID_TIERS,
    TIER_POINTS,
    RIVALRY_WEEK_NUMBERS,
    RIVALRY_GAME_POINTS,
    GAMES_PER_WEEK
)

from utils.ui_helpers import (
    dark_page_container
)


def admin_page():

    if not app.storage.user.get("is_admin"):
        ui.label("Administrator access required.")
        return

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

        weeks = get_all_weeks()
        week_number = ui.number(
            label="Week Number",
            value=weeks[0].week_number if weeks else 1,
            precision=0
        )

        game_inputs = []

        games_container = ui.column().classes(
            "w-full"
        )


        def groups_for_sport(selected_sport):
            if selected_sport == "nfl":
                return NFL_DIVISIONS
            if selected_sport == "nhl":
                return NHL_DIVISIONS
            return NCAA_CONFERENCES

        def group_for_team(selected_sport, team_name):
            for group_name, team_names in groups_for_sport(selected_sport).items():
                if team_name in team_names:
                    return group_name
            return None

        def add_game_input(game_number, existing_game=None):

            existing_sport = (existing_game.sport or "ncaa") if existing_game else "ncaa"
            existing_away = get_team_by_id(existing_game.away_team_id) if existing_game else None
            existing_home = get_team_by_id(existing_game.home_team_id) if existing_game else None

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
                            "nfl",
                            "nhl",
                        ],
                        value=existing_sport,
                        label="Sport"
                    )
        
                    away_conference = ui.select(
                        options=[],
                        label="Away Conference / Division"
                    )
        
                    away_team = ui.select(
                        options=[],
                        label="Away Team"
                    ).props(
                        "use-input"
                    )
        
                    home_conference = ui.select(
                        options=[],
                        label="Home Conference / Division"
                    )
        
                    home_team = ui.select(
                        options=[],
                        label="Home Team"
                    ).props(
                        "use-input"
                    )
        
                    def update_conferences():

                        available_groups = list(
                            groups_for_sport(sport.value).keys()
                        )
        
                        away_conference.set_options(
                            available_groups
                        )
        
                        home_conference.set_options(
                            available_groups
                        )
        
                        away_team.set_options([])
                        home_team.set_options([])
        
                    def update_away_teams():

                        away_team.set_options(
                            groups_for_sport(sport.value).get(
                                away_conference.value,
                                []
                            )
                        )
        
                    def update_home_teams():

                        home_team.set_options(
                            groups_for_sport(sport.value).get(
                                home_conference.value,
                                []
                            )
                        )
        
                    sport.on(
                        "update:model-value",
                        lambda e: update_conferences()
                    )
        
                    away_conference.on(
                        "update:model-value",
                        lambda e: update_away_teams()
                    )
        
                    home_conference.on(
                        "update:model-value",
                        lambda e: update_home_teams()
                    )
        
                    update_conferences()
        
                    tier = ui.select(
                        options=VALID_TIERS,
                        value=("F" if existing_game and existing_game.tier == "E" else (existing_game.tier if existing_game else "A")),
                        label="Tier"
                    )
        
                    result_label = ui.label(
                        ""
                    ).style(
                        "color: #d1d5db;"
                    )
        
                    game_data = {
                        "game_number": game_number,
                        "sport": sport,
                        "away_conference": away_conference,
                        "home_conference": home_conference,
                        "away_team": away_team,
                        "home_team": home_team,
                        "tier": tier,
                        "result_label": result_label,
                        "existing_game_id": existing_game.id if existing_game else None,
                    }
                    game_inputs.append(game_data)

                    if existing_game:
                        away_name = existing_away.team_name if existing_away else ""
                        home_name = existing_home.team_name if existing_home else ""
                        available_groups = groups_for_sport(existing_sport)
                        away_group = group_for_team(existing_sport, away_name)
                        home_group = group_for_team(existing_sport, home_name)

                        away_conference.set_options(list(available_groups.keys()))
                        home_conference.set_options(list(available_groups.keys()))
                        away_conference.set_value(away_group)
                        home_conference.set_value(home_group)
                        away_team.set_options(available_groups.get(away_group, [away_name] if away_name else []))
                        home_team.set_options(available_groups.get(home_group, [home_name] if home_name else []))
                        away_team.set_value(away_name)
                        home_team.set_value(home_name)

                        sport.disable()
                        away_conference.disable()
                        away_team.disable()
                        home_conference.disable()
                        home_team.disable()
                        tier.disable()
                        result_label.set_text("Existing game — preserved. Use Edit tier below if needed.")
                        result_label.style("color: #60a5fa;")

                    return game_data

        def rebuild_game_inputs():
            games_container.clear()
            game_inputs.clear()

            try:
                selected_week_number = int(week_number.value)
            except (TypeError, ValueError):
                selected_week_number = 1

            selected_week = next(
                (
                    existing_week
                    for existing_week in get_all_weeks()
                    if existing_week.week_number == selected_week_number
                ),
                None,
            )

            existing_games = get_games_by_week(selected_week.id) if selected_week else []
            for existing_game in existing_games:
                add_game_input(existing_game.game_number, existing_game=existing_game)

            next_number = max((game.game_number for game in existing_games), default=0) + 1
            blank_count = max(1, GAMES_PER_WEEK - len(existing_games))
            for offset in range(blank_count):
                add_game_input(next_number + offset)

        def add_extra_game():
            used_numbers = [item["game_number"] for item in game_inputs]
            add_game_input(max(used_numbers, default=0) + 1)

        week_number.on("update:model-value", lambda e: rebuild_game_inputs())
        rebuild_game_inputs()


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

        async def confirm_remove_game(game_id, matchup):
            with ui.dialog() as dialog, ui.card():
                ui.label(f"Remove {matchup}?").classes("text-h6")
                ui.label("This permanently removes the game and everyone's picks for it, including awarded points. Weekly bonuses and standings will be recalculated. If this is the first game, its tiebreaker guesses will be cleared.").classes("max-w-md")
                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=lambda: dialog.submit(False))
                    ui.button("Remove game", color="negative", on_click=lambda: dialog.submit(True))
            if await dialog:
                success, message = remove_game_as_admin(game_id, app.storage.user.get("user_id"))
                ui.notify(message, color="positive" if success else "negative")
                if success:
                    load_weeks()

        def edit_game_tier(game_id, current_tier, matchup, week_number):
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
                ui.label(f"Edit tier: {matchup}").classes("text-h6")
                tier_select = ui.select(
                    options={tier: f"{tier} — {TIER_POINTS[tier]} points" for tier in VALID_TIERS},
                    value="F" if current_tier == "E" else current_tier,
                    label="Game tier",
                ).classes("w-full")
                if week_number in RIVALRY_WEEK_NUMBERS:
                    ui.label(f"Rivalry week: every game remains worth {RIVALRY_GAME_POINTS} points regardless of tier.")
                ui.label("Saving recalculates awarded points, the weekly bonus, and the leaderboard. Players’ team selections stay the same.")

                def save_tier():
                    success, message = update_game_tier_as_admin(
                        game_id, tier_select.value, app.storage.user.get("user_id")
                    )
                    ui.notify(message, color="positive" if success else "negative")
                    if success:
                        dialog.close()
                        load_weeks()

                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=dialog.close)
                    ui.button("Save tier", on_click=save_tier)
            dialog.open()

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

                                ui.button(
                                    "Edit tier", icon="edit",
                                    on_click=lambda game_id=game.id, tier=game.tier, matchup=f"{away_name} vs {home_name}", number=week.week_number: edit_game_tier(game_id, tier, matchup, number),
                                )

                                ui.button(
                                    "Remove game", icon="delete", color="negative",
                                    on_click=lambda game_id=game.id, matchup=f"{away_name} vs {home_name}": confirm_remove_game(game_id, matchup),
                                ).classes("ml-auto")

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
            failed_games = 0

            for game_data in game_inputs:

                if game_data.get("existing_game_id"):
                    continue

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

                    away_updates = {
                        "espn_team_id": away_espn_data.get("espn_team_id"),
                        "abbreviation": away_espn_data.get("abbreviation"),
                        "record": away_espn_data.get("record"),
                        "sport": selected_sport,
                    }
                    home_updates = {
                        "espn_team_id": home_espn_data.get("espn_team_id"),
                        "abbreviation": home_espn_data.get("abbreviation"),
                        "record": home_espn_data.get("record"),
                        "sport": selected_sport,
                    }

                    # NHL logos are intentionally left to local assets supplied
                    # by the admin. Keep the existing NCAA/NFL logo behavior.
                    if selected_sport != "nhl":
                        away_logo_url = away_espn_data.get("logo")
                        home_logo_url = home_espn_data.get("logo")
                        if away_logo_url:
                            away_updates["logo_path"] = (
                                download_logo(away_logo_url, away_name)
                                or away_logo_url
                            )
                        if home_logo_url:
                            home_updates["logo_path"] = (
                                download_logo(home_logo_url, home_name)
                                or home_logo_url
                            )

                    update_team(away_team.id, **away_updates)
                    update_team(home_team.id, **home_updates)

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
                    game_number=None,
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
                    game_data["away_team"].set_value(None)
                    game_data["home_team"].set_value(None)
                else:
                    failed_games += 1
                    result_label.set_text("Unable to save game. Your entry has been kept; please try again.")
                    result_label.style("color: #ef4444;")

            ui.notify(
                f"{created_games} games saved. {failed_games} failed. {matched_games} ESPN matches, {unmatched_games} unmatched.",
                color="negative" if failed_games else "positive"
            )

            load_weeks()
            rebuild_game_inputs()

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

        ui.separator().style(
            "background-color: #333333; margin-top: 18px;"
        )
    
        def export_excel():

            success = export_picks_to_excel()

            if success:

                ui.download(
                    "picks_export.xlsx"
                )

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
