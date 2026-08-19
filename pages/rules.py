from nicegui import ui

from utils.ui_helpers import (
    dark_page_container
)


def rules_page():

    with dark_page_container():

        ui.label(
            "Master Plan - Football Season"
        ).style("""
            color: white;
            font-size: clamp(24px, 5vw, 36px);
            font-weight: bold;
        """)

        ui.label(
            "Rules, layout, and scoring structure for the DothPick football season."
        ).style(
            "color: #d1d5db;"
        )

        def section_card(title):

            card = ui.card().classes(
                "w-full"
            ).style(
                """
                background-color: #151515;
                color: white;
                border: 1px solid #333333;
                border-radius: 14px;
                padding: 18px;
                margin-top: 14px;
                """
            )

            with card:

                ui.label(
                    title
                ).classes(
                    "text-h5"
                ).style(
                    "color: white; font-weight: bold;"
                )

            return card

        def dark_table(headers, rows):

            html = """
            <table style="
                min-width: 900px;
                border-collapse: collapse;
                color: white;
                margin-top: 12px;
            ">
                <thead>
                    <tr>
            """

            for header in headers:

                html += f"""
                    <th style="
                        border: 1px solid #444444;
                        padding: 10px;
                        background-color: #202020;
                        color: white;
                        text-align: left;
                    ">
                        {header}
                    </th>
                """

            html += """
                    </tr>
                </thead>
                <tbody>
            """

            for row in rows:

                html += "<tr>"

                for cell in row:

                    html += f"""
                    <td style="
                        border: 1px solid #444444;
                        padding: 10px;
                        background-color: #111111;
                        color: white;
                    ">
                        {cell}
                    </td>
                    """

                html += "</tr>"

            html += """
                </tbody>
            </table>
            """

            ui.html(
                f"""
                <div style="
                    width: 100%;
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                ">
                    {html}
                </div>
                """
            )

        with section_card(
            "Weekly Points"
        ):

            dark_table(
                [
                    "Week #",
                    "Football Active",
                    "Game 1",
                    "Game 2",
                    "Game 3",
                    "Game 4",
                    "Game 5",
                    "Weekly Win Bonus"
                ],
                [
                    ["0", "CFB", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["1", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["2", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["3", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["4", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["5", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["6", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["7", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["8", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["9", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["10", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["11", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["12", "CFB + NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["13", "Rivalry Week", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["15", "NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["16", "NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["17", "NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"],
                    ["18", "NFL", "TBD", "TBD", "TBD", "TBD", "TBD", "5"]
                ]
            )

            ui.label(
                "Each week will have 5 games. Their point values depend on the tier ranking of the game decided the week prior to the game."
            ).style(
                "color: #d1d5db; margin-top: 10px;"
            )

            ui.label(
                "Total Possible Weekly Points: 90"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "Tier Ranking"
        ):

            dark_table(
                [
                    "Tier",
                    "Point Value",
                    "Note"
                ],
                [
                    ["S", "6", "ONLY for when 2 top 5 teams play"],
                    ["A", "5", ""],
                    ["B", "4", ""],
                    ["C", "3", ""],
                    ["D", "2", ""],
                    ["E", "1", ""],
                    ["TBD", "0", ""]
                ]
            )

        with section_card(
            "Special Points - Rivalry Week"
        ):

            ui.label(
                "Red text = CFB     Blue text = NFL"
            ).style(
                "color: #d1d5db;"
            )

            dark_table(
                [
                    "Game #",
                    "Game 1",
                    "Game 2",
                    "Game 3",
                    "Game 4",
                    "Game 5",
                    "Weekly Win Bonus",
                    "Tie Breaker"
                ],
                [
                    [
                        "Points",
                        "3",
                        "3",
                        "3",
                        "3",
                        "3",
                        "10*",
                        "Points Scored in Game 1"
                    ]
                ]
            )

            ui.label(
                "*The person with the most correct guesses wins a bonus of 10 points."
            ).style(
                "color: #d1d5db; margin-top: 10px;"
            )

            ui.label(
                "If 2 players are tied with the same number of correct guesses, the person who guesses the more accurate total points score in Game 1 receives 7 bonus points, and the less accurate guesser receives 3 bonus points."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "Total Possible Points: 25"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "Conference Championships"
        ):

            ui.label(
                "There will be 3 polls for Conference Champions: prior to Week 0, prior to Week 10, and after the teams in the Conference Championship have been selected."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "You cannot choose a team more than once, so each person must choose a different team for preseason, midseason, and postseason guesses."
            ).style(
                "color: #d1d5db;"
            )

            dark_table(
                [
                    "Conference",
                    "Big10",
                    "SEC",
                    "ACC",
                    "Big12"
                ],
                [
                    ["Preseason Guess Points", "9", "9", "7", "7"],
                    ["Midseason Guess Points", "7", "7", "5", "5"],
                    ["Postseason Guess Points", "5", "5", "4", "4"]
                ]
            )

            ui.label(
                "The person that accumulates the most points from their 3 guesses will be awarded a bonus of 10 points."
            ).style(
                "color: #d1d5db; margin-top: 10px;"
            )

            ui.label(
                "Total Possible Points: 32"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "CFP Playoff Points"
        ):

            dark_table(
                [
                    "Round",
                    "Games",
                    "Point Value"
                ],
                [
                    ["First Round", "Game 1, Game 2, Game 3, Game 4", "2"],
                    ["Quarterfinals", "Game 1, Game 2, Game 3, Game 4", "4"],
                    ["Semifinals", "Game 1, Game 2", "6"],
                    ["Champion", "Game 1", "15"]
                ]
            )

            ui.label(
                "The person that accumulates the most points during the playoffs will be awarded a bonus of 15 points."
            ).style(
                "color: #d1d5db; margin-top: 10px;"
            )

            ui.label(
                "Total Possible Points: 42"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "CFP Preseason Champion Points"
        ):

            ui.label(
                "Each person will choose 3 teams prior to Week 0 that they believe can win the CFP. They will rank them 1-3 by confidence, with 1 being the most confident."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "For preseason picks, a first round bye counts the same as a win in the First Round."
            ).style(
                "color: #d1d5db;"
            )

            dark_table(
                [
                    "Team Ranking",
                    "Did Not Qualify",
                    "Round 1",
                    "Quarterfinals",
                    "Semifinals",
                    "Championship",
                    "Champion"
                ],
                [
                    ["Team 1", "-3", "3", "6", "9", "12", "20"],
                    ["Team 2", "-2", "2", "4", "6", "8", "15"],
                    ["Team 3", "-1", "1", "2", "4", "6", "10"]
                ]
            )

            ui.label(
                "Total Possible Points: 32"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "NFL Playoff Points"
        ):

            dark_table(
                [
                    "Elimination Round",
                    "Games",
                    "Point Value Per Correct Guess"
                ],
                [
                    ["Wild Card", "Game 1, Game 2, Game 3, Game 4, Game 5, Game 6", "2"],
                    ["Divisional", "Game 1, Game 2, Game 3, Game 4", "4"],
                    ["Conference", "AFC Champ, NFC Champ", "6"],
                    ["Super Bowl", "SUPER BOWL", "12"]
                ]
            )

            ui.label(
                "The person that accumulates the most points over the NFL playoffs will earn a 10 point bonus."
            ).style(
                "color: #d1d5db; margin-top: 10px;"
            )

            ui.label(
                "Total Possible Points: 62"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "NFL Preseason Champion Points"
        ):

            ui.label(
                "Each person will choose 2 AFC and 2 NFC teams prior to Week 1 of the NFL season that they believe can win the Super Bowl."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "They will rank them 1-4, with no stipulation on conference for their rankings."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "For preseason picks, a first round bye counts the same as a win in the Wild Card Round."
            ).style(
                "color: #d1d5db;"
            )

            dark_table(
                [
                    "Team Ranking",
                    "Did Not Qualify",
                    "Wild Card Round",
                    "Divisional Round",
                    "Conference Championship",
                    "Super Bowl",
                    "Champion"
                ],
                [
                    ["Team 1", "-5", "4", "8", "12", "15", "20"],
                    ["Team 2", "-4", "3", "6", "9", "12", "18"],
                    ["Team 3", "-3", "2", "4", "6", "8", "12"],
                    ["Team 4", "-2", "1", "3", "5", "7", "10"]
                ]
            )

            ui.label(
                "Total Possible Points: 43"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "NFL Midseason and Postseason Championship Points"
        ):

            ui.label(
                "Prior to Week 10 and prior to the start of the playoffs, each person will choose an AFC team and an NFC team they believe can win the Super Bowl."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "Midseason Guess Points"
            ).classes(
                "text-h6"
            ).style(
                "color: white; margin-top: 10px;"
            )

            dark_table(
                [
                    "Team",
                    "Elimination Round",
                    "Point Value, NO BYE",
                    "Point Value, WITH BYE"
                ],
                [
                    ["AFC Guess", "Did not qualify for playoffs", "-10", ""],
                    ["AFC Guess", "Wild Card Round", "0", "-5"],
                    ["AFC Guess", "Divisional Round", "3", "3"],
                    ["AFC Guess", "Conference Championship", "6", "6"],
                    ["AFC Guess", "Super Bowl", "9", "9"],
                    ["AFC Guess", "Champion", "15", "15"],
                    ["NFC Guess", "Did not qualify for playoffs", "-10", ""],
                    ["NFC Guess", "Wild Card Round", "0", "-5"],
                    ["NFC Guess", "Divisional Round", "3", "3"],
                    ["NFC Guess", "Conference Championship", "6", "6"],
                    ["NFC Guess", "Super Bowl", "9", "9"],
                    ["NFC Guess", "Champion", "15", "15"]
                ]
            )

            ui.label(
                "Postseason Guess Points"
            ).classes(
                "text-h6"
            ).style(
                "color: white; margin-top: 14px;"
            )

            dark_table(
                [
                    "Team",
                    "Elimination Round",
                    "Point Value, NO BYE",
                    "Point Value, WITH BYE"
                ],
                [
                    ["AFC Guess", "Wild Card Round", "-8", ""],
                    ["AFC Guess", "Divisional Round", "0", "-8"],
                    ["AFC Guess", "Conference Championship", "3", "3"],
                    ["AFC Guess", "Super Bowl", "6", "6"],
                    ["AFC Guess", "Champion", "12", "12"],
                    ["NFC Guess", "Wild Card Round", "-8", ""],
                    ["NFC Guess", "Divisional Round", "0", "-8"],
                    ["NFC Guess", "Conference Championship", "3", "3"],
                    ["NFC Guess", "Super Bowl", "6", "6"],
                    ["NFC Guess", "Champion", "12", "12"]
                ]
            )

            ui.label(
                "Total Possible Points: 42"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )

        with section_card(
            "Preseason Conference Champion"
        ):

            ui.label(
                "Prior to Week 1 of the NFL season, each person will choose a team that they believe will win its division."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "Each correct guess will earn the person 4 points."
            ).style(
                "color: #d1d5db;"
            )

            ui.label(
                "Total Possible Points: 32"
            ).style(
                "color: #22c55e; font-weight: bold;"
            )