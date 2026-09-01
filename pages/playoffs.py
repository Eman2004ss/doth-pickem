from nicegui import app, ui

from services.logo_service import get_logo_path_by_name
from services.playoff_service import (
    BRACKETS,
    get_bracket,
    get_user_playoff_picks,
    save_playoff_game,
    save_playoff_pick,
)
from utils.ui_helpers import dark_page_container


CARD = "background-color:#151515;color:white;border:1px solid #333;border-radius:14px;padding:18px;margin-top:12px;"

ROUND_COLUMN = "display:flex;flex-direction:column;align-items:center;gap:24px;min-width:170px;"

GAME_BOX = "background-color:#1e1e1e;border:1px solid #333;border-radius:10px;padding:10px;width:150px;"

TEAM_ROW = "display:flex;align-items:center;justify-content:center;padding:6px;border-radius:8px;cursor:pointer;"

TEAM_ROW_SELECTED = TEAM_ROW + "border:2px solid #22c55e;background-color:#14532d;"

TEAM_ROW_UNSELECTED = TEAM_ROW + "border:2px solid transparent;"

TEAM_ROW_LOCKED = "display:flex;align-items:center;justify-content:center;padding:6px;border-radius:8px;border:2px solid transparent;"


def playoffs_page():
    with dark_page_container():
        with ui.row().classes("w-full items-center justify-between wrap"):
            ui.label("Playoff Brackets").classes("text-h3").style("color:white;")
            with ui.row():
                ui.button("Weekly Picks", on_click=lambda: ui.navigate.to("/weekly-picks"))
                ui.button("Home", on_click=lambda: ui.navigate.to("/home"))

        user_id = app.storage.user.get("user_id")
        is_admin = bool(app.storage.user.get("is_admin", False))

        ui.label("Click a team's logo to pick who you think wins that game.").style("color:#9ca3af;")

        sport_toggle = ui.toggle({"cfb": "CFP (College)", "nfl": "NFL"}, value="cfb")
        bracket_container = ui.row().classes("w-full items-start justify-center wrap")

        def team_logo(team_name):
            return get_logo_path_by_name(team_name)

        def render():
            bracket_container.clear()
            sport = sport_toggle.value or "cfb"
            bracket = get_bracket(sport)
            my_picks = get_user_playoff_picks(user_id, sport) if user_id else {}

            with bracket_container:
                for round_data in bracket:
                    round_key = round_data["round_key"]
                    with ui.column().style(ROUND_COLUMN):
                        ui.label(round_data["label"]).style("color:white;font-weight:bold;")
                        for game in round_data["games"]:
                            slot = game["slot"]
                            picked = my_picks.get((round_key, slot))
                            with ui.column().style(GAME_BOX):
                                ui.label(f"Game {slot}").style("color:#6b7280;font-size:0.75rem;")
                                for team in (game["team1"], game["team2"]):
                                    is_tbd = not team or team.strip().upper() == "TBD"
                                    is_selected = picked == team

                                    def on_pick(
                                        team=team,
                                        sport=sport,
                                        round_key=round_key,
                                        slot=slot,
                                    ):
                                        if not user_id:
                                            ui.notify("Log in to make playoff picks.", color="negative")
                                            return
                                        success, message = save_playoff_pick(
                                            user_id, sport, round_key, slot, team
                                        )
                                        ui.notify(message, color="positive" if success else "negative")
                                        if success:
                                            render()

                                    row_style = TEAM_ROW_LOCKED if is_tbd else (
                                        TEAM_ROW_SELECTED if is_selected else TEAM_ROW_UNSELECTED
                                    )

                                    with ui.row().style(row_style).on(
                                        "click", None if is_tbd else on_pick
                                    ):
                                        ui.image(team_logo(team)).style(
                                            "width:44px;height:44px;object-fit:contain;"
                                        )

        sport_toggle.on("update:model-value", lambda e: render())
        render()

        if is_admin:
            with ui.expansion("Admin: Enter Playoff Teams & Results", icon="edit").classes("w-full").style(CARD):
                admin_sport_toggle = ui.toggle({"cfb": "CFP (College)", "nfl": "NFL"}, value="cfb")
                admin_container = ui.column().classes("w-full")

                def render_admin():
                    admin_container.clear()
                    sport = admin_sport_toggle.value or "cfb"
                    bracket = get_bracket(sport)

                    with admin_container:
                        for round_data in bracket:
                            with ui.card().classes("w-full").style(CARD):
                                ui.label(round_data["label"]).classes("text-h6").style("color:white;")
                                with ui.row().classes("w-full wrap"):
                                    for game in round_data["games"]:
                                        with ui.column().style(
                                            "background-color:#1e1e1e;border:1px solid #333;"
                                            "border-radius:10px;padding:14px;margin:6px;min-width:220px;"
                                        ):
                                            ui.label(f"Game {game['slot']}").style("color:#9ca3af;font-size:0.85rem;")
                                            team1_input = ui.input(label="Team 1", value=game["team1"]).classes("w-full")
                                            team2_input = ui.input(label="Team 2", value=game["team2"]).classes("w-full")
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
                                                render_admin()
                                                render()

                                            ui.button("Save", on_click=save).classes("w-full")

                admin_sport_toggle.on("update:model-value", lambda e: render_admin())
                render_admin()
