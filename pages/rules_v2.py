from nicegui import ui
from utils.ui_helpers import dark_page_container


CARD = "background-color:#151515;color:white;border:1px solid #333;border-radius:14px;padding:18px;margin-top:12px;"


def _table(columns, rows):
    ui.table(
        columns=[{"name": str(i), "label": label, "field": str(i), "align": "left"} for i, label in enumerate(columns)],
        rows=[{str(i): value for i, value in enumerate(row)} for row in rows],
        row_key="0",
    ).classes("w-full").style("background:#202020;color:white;")


def rules_page():
    with dark_page_container():
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Rules & Scoring").classes("text-h3").style("color:white;")
            ui.button("Home", on_click=lambda: ui.navigate.to("/home"))

        with ui.card().classes("w-full").style(CARD):
            ui.label("Weekly Game Tiers").classes("text-h5").style("color:white;font-weight:bold;")
            _table(
                ["Tier", "Points", "Note"],
                [
                    ["S", 6, "Only for a Top-5 vs Top-5 matchup"],
                    ["A", 5, ""],
                    ["B", 4, ""],
                    ["C", 3, ""],
                    ["D", 2, ""],
                    ["F", 1, "Renamed from E; point value is unchanged"],
                    ["TBD", 0, ""],
                ],
            )
            ui.label("Regular weekly winner bonus: 5 points. Ties are resolved by the predicted total points in Game 1.").style("color:#d1d5db;")

        with ui.card().classes("w-full").style(CARD):
            ui.label("Rivalry Week - Week 13").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Every game is worth 3 points, regardless of the normal tier.").style("color:#d1d5db;")
            ui.label("Most correct picks: 10-point bonus. If the lead is tied, Game 1 total points is the tiebreaker: closer guess gets 7 and the next gets 3.").style("color:#d1d5db;")
            ui.label("The tiebreaker locks at kickoff of Game 1.").style("color:#facc15;font-weight:bold;")

        with ui.card().classes("w-full").style(CARD):
            ui.label("CFB Conference Champion Picks").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Polls: preseason (before Week 0), midseason (before Week 10), postseason (after championship teams are selected, before the games). A team cannot be reused for the same conference across the three polls.").style("color:#d1d5db;")
            _table(
                ["Period", "Big Ten", "SEC", "ACC", "Big 12"],
                [
                    ["Preseason", 9, 9, 7, 7],
                    ["Midseason", 7, 7, 5, 5],
                    ["Postseason", 5, 5, 4, 4],
                ],
            )
            ui.label("Highest accumulated conference-prediction score receives a 10-point bonus.").style("color:#d1d5db;")

        with ui.card().classes("w-full").style(CARD):
            ui.label("CFP Preseason Champion Picks").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Choose and rank 3 teams before Week 0. Rank 1 is most confident. A first-round bye counts as a Round 1 win.").style("color:#d1d5db;")
            _table(
                ["Rank", "DNQ", "Round 1", "Quarterfinal", "Semifinal", "Championship", "Champion"],
                [
                    [1, -3, 3, 6, 9, 12, 20],
                    [2, -2, 2, 4, 6, 8, 15],
                    [3, -1, 1, 2, 4, 6, 10],
                ],
            )

        with ui.card().classes("w-full").style(CARD):
            ui.label("NFL Preseason Super Bowl Picks").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Choose 2 AFC and 2 NFC teams before NFL Week 1, then rank all four 1-4. A first-round bye counts as a Wild Card win.").style("color:#d1d5db;")
            _table(
                ["Rank", "DNQ", "Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"],
                [
                    [1, -5, 4, 8, 12, 15, 20],
                    [2, -4, 3, 6, 9, 12, 18],
                    [3, -3, 2, 4, 6, 8, 12],
                    [4, -2, 1, 3, 5, 7, 10],
                ],
            )

        with ui.card().classes("w-full").style(CARD):
            ui.label("NFL Midseason & Postseason Super Bowl Picks").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Choose one AFC and one NFC team before Week 10, then again before the playoffs.").style("color:#d1d5db;")
            _table(
                ["Midseason result", "No bye", "With bye"],
                [
                    ["Did not qualify", -10, -10], ["Wild Card", 0, -5], ["Divisional", 3, 3],
                    ["Conference", 6, 6], ["Super Bowl", 9, 9], ["Champion", 15, 15],
                ],
            )
            _table(
                ["Postseason result", "No bye", "With bye"],
                [
                    ["Wild Card / DNQ", -8, -8], ["Divisional", 0, -8], ["Conference", 3, 3],
                    ["Super Bowl", 6, 6], ["Champion", 12, 12],
                ],
            )

        with ui.card().classes("w-full").style(CARD):
            ui.label("NFL Preseason Division Champions").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Choose the winner of all 8 NFL divisions before Week 1. Each correct division winner is worth 4 points (32 possible).").style("color:#d1d5db;")

        with ui.card().classes("w-full").style(CARD):
            ui.label("Playoff Game Picks").classes("text-h5").style("color:white;font-weight:bold;")
            _table(["CFP Round", "Points per correct pick"], [["First Round", 2], ["Quarterfinal", 4], ["Semifinal", 6], ["Champion", 15]])
            ui.label("CFP playoff points leader bonus: 15.").style("color:#d1d5db;")
            _table(["NFL Round", "Points per correct pick"], [["Wild Card", 2], ["Divisional", 4], ["Conference", 6], ["Super Bowl", 12]])
            ui.label("NFL playoff points leader bonus: 10.").style("color:#d1d5db;")
