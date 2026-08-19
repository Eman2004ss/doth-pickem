import requests

from database.db import SessionLocal

from database.models import (
    Team,
    Game
)


NCAA_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "football/college-football/scoreboard"
)

NFL_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "football/nfl/scoreboard"
)


def get_scoreboard(
    sport="ncaa"
):

    selected_sport = (
        sport
        or "ncaa"
    ).lower()

    if selected_sport == "nfl":

        url = NFL_SCOREBOARD_URL

    else:

        url = NCAA_SCOREBOARD_URL

    try:

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None


def normalize_team_name(team_name):

    if not team_name:
        return ""

    return (
        team_name
        .strip()
        .lower()
    )


def get_team_record_from_competitor(
    competitor
):

    records = competitor.get(
        "records",
        []
    )

    if not records:
        return ""

    return (
        records[0]
        .get(
            "summary",
            ""
        )
    )


def get_team_logo_from_competitor(
    competitor
):

    team = competitor.get(
        "team",
        {}
    )

    logos = team.get(
        "logos",
        []
    )

    if not logos:
        return None

    return logos[0].get(
        "href"
    )


def get_team_data_from_competitor(
    competitor
):

    team = competitor.get(
        "team",
        {}
    )

    return {
        "team_name": team.get(
            "displayName",
            ""
        ),
        "espn_team_id": team.get(
            "id"
        ),
        "abbreviation": team.get(
            "abbreviation"
        ),
        "record": get_team_record_from_competitor(
            competitor
        ),
        "logo": get_team_logo_from_competitor(
            competitor
        )
    }


def find_event_by_teams(
    away_team_name,
    home_team_name,
    sport="ncaa"
):

    selected_sport = (
        sport
        or "ncaa"
    ).lower()

    scoreboard = get_scoreboard(
        selected_sport
    )

    if not scoreboard:
        return None

    target_away = normalize_team_name(
        away_team_name
    )

    target_home = normalize_team_name(
        home_team_name
    )

    for event in scoreboard.get(
        "events",
        []
    ):

        competition = (
            event.get(
                "competitions",
                [{}]
            )[0]
        )

        competitors = competition.get(
            "competitors",
            []
        )

        away_data = None
        home_data = None

        for competitor in competitors:

            competitor_type = competitor.get(
                "homeAway"
            )

            team_data = get_team_data_from_competitor(
                competitor
            )

            if competitor_type == "away":

                away_data = team_data

            elif competitor_type == "home":

                home_data = team_data

        if not away_data or not home_data:
            continue

        current_away = normalize_team_name(
            away_data["team_name"]
        )

        current_home = normalize_team_name(
            home_data["team_name"]
        )

        if (
            current_away == target_away
            and
            current_home == target_home
        ):

            status_type = (
                event.get(
                    "status",
                    {}
                )
                .get(
                    "type",
                    {}
                )
            )

            return {
                "event_id": event.get(
                    "id"
                ),
                "kickoff": event.get(
                    "date"
                ),
                "away_team": away_data,
                "home_team": home_data,
                "sport": selected_sport,
                "status": status_type.get(
                    "description",
                    "Scheduled"
                )
            }

    return None


def update_team_from_espn_data(
    team_id,
    team_data,
    sport="ncaa"
):

    db = SessionLocal()

    try:

        team = (
            db.query(Team)
            .filter(
                Team.id == team_id
            )
            .first()
        )

        if not team:
            return False

        team.espn_team_id = team_data.get(
            "espn_team_id"
        )

        team.abbreviation = team_data.get(
            "abbreviation"
        )

        team.record = team_data.get(
            "record"
        )

        team.logo_path = team_data.get(
            "logo"
        )

        team.sport = (
            sport
            or "ncaa"
        ).lower()

        team.source = "espn"

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_all_team_info(
    sport="ncaa"
):

    selected_sport = (
        sport
        or "ncaa"
    ).lower()

    scoreboard = get_scoreboard(
        selected_sport
    )

    if not scoreboard:
        return False

    db = SessionLocal()

    try:

        teams = (
            db.query(Team)
            .filter(
                Team.sport == selected_sport
            )
            .all()
        )

        for event in scoreboard.get(
            "events",
            []
        ):

            competition = (
                event.get(
                    "competitions",
                    [{}]
                )[0]
            )

            competitors = competition.get(
                "competitors",
                []
            )

            for competitor in competitors:

                api_team = competitor.get(
                    "team",
                    {}
                )

                api_team_name = api_team.get(
                    "displayName",
                    ""
                )

                for database_team in teams:

                    if (
                        normalize_team_name(
                            database_team.team_name
                        )
                        !=
                        normalize_team_name(
                            api_team_name
                        )
                    ):
                        continue

                    database_team.espn_team_id = api_team.get(
                        "id"
                    )

                    database_team.abbreviation = api_team.get(
                        "abbreviation"
                    )

                    database_team.record = get_team_record_from_competitor(
                        competitor
                    )

                    database_team.logo_path = get_team_logo_from_competitor(
                        competitor
                    )

                    database_team.sport = selected_sport
                    database_team.source = "espn"

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def get_event_by_id(
    espn_event_id,
    sport="ncaa"
):

    selected_sport = (
        sport
        or "ncaa"
    ).lower()

    scoreboard = get_scoreboard(
        selected_sport
    )

    if not scoreboard:
        return None

    for event in scoreboard.get(
        "events",
        []
    ):

        if (
            str(
                event.get(
                    "id"
                )
            )
            ==
            str(
                espn_event_id
            )
        ):

            return event

    return None


def update_game_from_espn(
    game_id,
    sport="ncaa"
):

    selected_sport = (
        sport
        or "ncaa"
    ).lower()

    db = SessionLocal()

    try:

        game = (
            db.query(Game)
            .filter(
                Game.id == game_id
            )
            .first()
        )

        if not game:
            return False

        if not game.espn_event_id:
            return False

        game_sport = (
            game.sport
            or selected_sport
            or "ncaa"
        ).lower()

        event = get_event_by_id(
            game.espn_event_id,
            game_sport
        )

        if not event:
            return False

        competition = (
            event.get(
                "competitions",
                [{}]
            )[0]
        )

        competitors = competition.get(
            "competitors",
            []
        )

        for competitor in competitors:

            try:

                score = int(
                    competitor.get(
                        "score",
                        0
                    )
                )

            except Exception:

                score = 0

            if competitor.get(
                "homeAway"
            ) == "home":

                game.home_score = score

            elif competitor.get(
                "homeAway"
            ) == "away":

                game.away_score = score

        status_type = (
            event.get(
                "status",
                {}
            )
            .get(
                "type",
                {}
            )
        )

        game.game_status = status_type.get(
            "description",
            "Scheduled"
        )

        game.game_clock = status_type.get(
            "detail",
            ""
        )

        game.sport = game_sport

        completed = status_type.get(
            "completed",
            False
        )

        if completed or game.game_status == "Final":

            game.completed = True
            game.game_status = "Final"

            if game.home_score > game.away_score:

                game.winner_team_id = game.home_team_id

            elif game.away_score > game.home_score:

                game.winner_team_id = game.away_team_id

            else:

                game.winner_team_id = None

        else:

            game.completed = False

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


def update_all_games_from_espn():

    db = SessionLocal()

    try:

        games = (
            db.query(Game)
            .filter(
                Game.espn_event_id.isnot(None)
            )
            .all()
        )

        updated_count = 0

        for game in games:

            sport = (
                game.sport
                if game.sport
                else "ncaa"
            )

            success = update_game_from_espn(
                game.id,
                sport
            )

            if success:

                updated_count += 1

        return updated_count

    finally:

        db.close()