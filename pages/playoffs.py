from nicegui import app, ui

from services.playoff_service import BRACKETS, get_bracket, save_playoff_game
from utils.ui_helpers import dark_page_container


CARD = "background-color:#151515;color:white;border:1px solid #333;border-radius:14px;padding:18px;margin-top:12px;"
GAME_CARD = "background-color:#1e1e1e;border:1px solid #333;border-radius:10px;padding:14px;margin:8px;min-width:220px;"


def playoffs_page():
    with dark_page_container():
        with ui.row().classes("w-full items-center justify-between wrap"):
            ui.label("Playoff Brackets").classes("text-h3").style("color:white;")
            with ui.row():
                ui.button("Weekly Picks", on_click=lambda: ui.navigate.to("/weekly-picks"))
                ui.button("Home", on_click=lambda: ui.navigate.to("/home"))

        is_admin = bool(app.storage.user.get("is_admin", False))

        sport_toggle = ui.toggle({"cfb": "CFP (College)", "nfl": "NFL"}, value="cfb")
        bracket_container = ui.column().classes("w-full")

        def render():
            bracket_container.clear()
            sport = sport_toggle.value or "cfb"
            bracket = get_bracket(sport)

            with bracket_container:
                for round_data in bracket:
                    with ui.card().classes("w-full").style(CARD):
                        ui.label(round_data["label"]).classes("text-h5").style("color:white;font-weight:bold;")
                        with ui.row().classes("w-full wrap"):
                            for game in round_data["games"]:
                                with ui.column().style(GAME_CARD):
                                    ui.label(f"Game {game['slot']}").style("color:#9ca3af;font-size:0.85rem;")

                                    if not is_admin:
                                        ui.label(game["team1"]).style("color:white;font-weight:bold;")
                                        ui.label("vs").style("color:#6b7280;")
                                        ui.label(game["team2"]).style("color:white;font-weight:bold;")
                                        if game["winner"]:
                                            ui.label(f"Winner: {game['winner']}").style("color:#22c55e;")
                                    else:
                                        team1_input = ui.input(
                                            label="Team 1", value=game["team1"]
                                        ).classes("w-full")
                                        team2_input = ui.input(
                                            label="Team 2", value=game["team2"]
                                        ).classes("w-full")
                                        winner_input = ui.input(
                                            label="Winner (optional)", value=game["winner"] or ""
                                        ).classes("w-full")

                                        def save(
                                            sport=sport,
                                            round_key=round_data["round_key"],
                                            slot=game["slot"],
                                            team1_input=team1_input,
                                            team2_input=team2_input,
                                            winner_input=winner_input,
                                        ):
                                            success, message = save_playoff_game(
                                                sport,
                                                round_key,
                                                slot,
                                                team1_input.value,
                                                team2_input.value,
                                                winner_input.value,
                                            )
                                            ui.notify(message, color="positive" if success else "negative")
                                            render()

                                        ui.button("Save", on_click=save).classes("w-full")

        sport_toggle.on("update:model-value", lambda e: render())
        render()