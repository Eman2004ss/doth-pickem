from nicegui import app, ui

from services.game_service import get_games_by_week
from services.locking_service import is_game_locked
from services.logo_service import get_local_logo_path
from services.pick_service import create_pick, get_user_pick, update_pick
from services.team_service import get_team_by_id
from services.tiebreaker_service import get_tiebreaker, is_tiebreaker_locked, save_tiebreaker
from services.week_service import get_all_weeks
from utils.constants import RIVALRY_GAME_POINTS, RIVALRY_WEEK_NUMBERS
from utils.ui_helpers import dark_page_container


CARD = "background-color:#151515;color:white;border:1px solid #333;border-radius:14px;padding:18px;"
TEAM_CARD = "background-color:#202020;color:white;border:1px solid #3a3a3a;border-radius:14px;padding:16px;width:100%;"


def weekly_picks_page():
    with dark_page_container():
        with ui.row().classes("w-full items-center justify-between wrap"):
            ui.label("Weekly Picks").classes("text-h3").style("color:white;")
            with ui.row():
                ui.button("Special Picks", on_click=lambda: ui.navigate.to("/special-picks"))
                ui.button("Home", on_click=lambda: ui.navigate.to("/home"))

        user_id = app.storage.user.get("user_id")
        if not user_id:
            ui.label("Please log in first.").style("color:white;")
            ui.button("Go To Login", on_click=lambda: ui.navigate.to("/"))
            return

        weeks = get_all_weeks()
        week_options = {f"Week {week.week_number}": week.id for week in weeks}
        weeks_by_id = {week.id: week for week in weeks}

        week_select = ui.select(
            options=list(week_options.keys()),
            label="Select Week",
        ).style("color:white; min-width:180px;")
        content = ui.column().classes("w-full")

        def logo_source(team):
            if not team:
                return None
            return "/" + get_local_logo_path(team.team_name)

        def save_pick(game_id, team_id):
            if is_game_locked(game_id):
                ui.notify("Game Locked", color="negative")
                return
            existing = get_user_pick(user_id, game_id)
            if existing:
                success = update_pick(user_id, game_id, team_id)
                ui.notify("Pick Updated" if success else "Game Locked", color="positive" if success else "negative")
            else:
                created = create_pick(user_id, game_id, team_id)
                ui.notify("Pick Saved" if created else "Unable to save pick", color="positive" if created else "negative")
            load_games()

        def team_pick_card(team, button_text, game, locked):
            with ui.card().style(TEAM_CARD):
                with ui.row().classes("w-full items-center wrap").style("gap:20px;"):
                    logo = logo_source(team)
                    if logo:
                        with ui.element("div").style(
                            "width:min(110px,24vw);height:min(110px,24vw);flex-shrink:0;display:flex;align-items:center;justify-content:center;"
                        ):
                            ui.image(logo).style("max-width:100%;max-height:100%;object-fit:contain;background:transparent;")
                    with ui.column().style("min-width:0;flex:1;"):
                        ui.label(team.team_name).style("color:white;font-weight:bold;font-size:18px;white-space:normal;")
                        ui.label(team.record or "Record Unavailable").style("color:#d1d5db;")
                        button = ui.button(button_text, on_click=lambda: save_pick(game.id, team.id))
                        if locked:
                            button.disable()

        def render_tiebreaker(week_id, games):
            game_one = sorted(games, key=lambda game: (game.game_number, game.id))[0]
            away = get_team_by_id(game_one.away_team_id)
            home = get_team_by_id(game_one.home_team_id)
            current = get_tiebreaker(user_id, week_id)
            locked = is_tiebreaker_locked(week_id)

            with ui.card().classes("w-full").style(CARD + "border-left:6px solid #facc15;"):
                ui.label("Weekly Tiebreaker").classes("text-h5").style("color:white;font-weight:bold;")
                if away and home:
                    ui.label(
                        f"Predict the TOTAL points scored in Game 1: {away.team_name} vs {home.team_name}"
                    ).style("color:#d1d5db;")
                ui.label("This locks exactly when Game 1 kicks off.").style("color:#9ca3af;")

                value = current.predicted_total if current else None
                total_input = ui.number(
                    label="Predicted Game 1 total points",
                    value=value,
                    min=0,
                    max=250,
                    precision=0,
                ).style("width:280px;")

                def save_total():
                    success, message = save_tiebreaker(user_id, week_id, total_input.value)
                    ui.notify(message, color="positive" if success else "negative")
                    if success:
                        load_games()

                button = ui.button("Save Tiebreaker", on_click=save_total)
                if locked:
                    total_input.disable()
                    button.disable()
                    ui.label("LOCKED").style("color:#ef4444;font-weight:bold;")
                elif current:
                    ui.label(f"Current prediction: {current.predicted_total} points").style("color:#22c55e;font-weight:bold;")

        def load_games():
            content.clear()
            if not week_select.value:
                return
            week_id = week_options[week_select.value]
            week = weeks_by_id.get(week_id)
            games = get_games_by_week(week_id)

            with content:
                if not games:
                    ui.label("No games created for this week.").style("color:white;")
                    return

                if week and week.week_number in RIVALRY_WEEK_NUMBERS:
                    with ui.card().classes("w-full").style(CARD + "border-left:6px solid #ef4444;"):
                        ui.label("RIVALRY WEEK").classes("text-h5").style("color:#ef4444;font-weight:bold;")
                        ui.label(
                            f"All five games are worth {RIVALRY_GAME_POINTS} points each. The weekly bonus is 10 points outright; a tie uses the Game 1 total-points tiebreaker (7/3)."
                        ).style("color:#d1d5db;")

                render_tiebreaker(week_id, games)

                for game in games:
                    home_team = get_team_by_id(game.home_team_id)
                    away_team = get_team_by_id(game.away_team_id)
                    if not home_team or not away_team:
                        continue
                    current_pick = get_user_pick(user_id, game.id)
                    locked = is_game_locked(game.id)

                    with ui.card().classes("w-full").style(CARD):
                        ui.label(f"Game {game.game_number}: {away_team.team_name} vs {home_team.team_name}").classes("text-h5").style("color:white;")
                        if week and week.week_number in RIVALRY_WEEK_NUMBERS:
                            ui.label(f"Rivalry scoring: {RIVALRY_GAME_POINTS} points").style("color:#facc15;font-weight:bold;")
                        else:
                            ui.label(f"{game.tier} Tier").style("color:#d1d5db;")
                        if locked:
                            ui.label("LOCKED").style("color:#ef4444;font-weight:bold;")

                        with ui.row().classes("w-full items-stretch wrap").style("gap:14px;"):
                            with ui.column().style("flex:1;min-width:280px;"):
                                team_pick_card(away_team, "Pick Away Team", game, locked)
                            with ui.column().style("flex:1;min-width:280px;"):
                                team_pick_card(home_team, "Pick Home Team", game, locked)

                        if current_pick:
                            selected = get_team_by_id(current_pick.selected_team_id)
                            if selected:
                                ui.label(f"Your Pick: {selected.team_name}").style("color:#22c55e;font-weight:bold;")

        week_select.on("update:model-value", lambda e: load_games())
        if week_options:
            first_week = list(week_options.keys())[0]
            week_select.set_value(first_week)
            load_games()
