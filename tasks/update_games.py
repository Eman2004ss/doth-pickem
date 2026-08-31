"""Repair missing ESPN links and refresh all linked games.

The original updater skipped every Game whose espn_event_id was NULL.  That
meant a game saved while ESPN's default scoreboard did not include the future
matchup could never repair itself later.  This task first tries to relink those
games using the season-wide finder installed by services.espn_compat, then
runs the normal ESPN updater for every linked game.
"""

from datetime import datetime, timezone

from database.db import SessionLocal
from database.models import Game
from services.espn_compat import install_espn_patches

# Also make this task safe when run directly from the command line instead of
# through app.py.
install_espn_patches()

from services.espn_service import find_event_by_teams, update_game_from_espn


def _parse_kickoff(raw):
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except Exception:
        return None


def _apply_team_data(team, data, sport):
    if not team or not data:
        return
    if data.get("espn_team_id"):
        team.espn_team_id = str(data["espn_team_id"])
    if data.get("abbreviation"):
        team.abbreviation = data["abbreviation"]
    if data.get("record") is not None:
        team.record = data.get("record") or ""
    if data.get("logo"):
        team.logo_path = data["logo"]
    team.sport = sport
    team.source = "espn"


def repair_unlinked_games():
    """Try to attach ESPN event IDs to previously-unmatched future games."""
    db = SessionLocal()
    repaired_ids = []
    try:
        games = (
            db.query(Game)
            .filter(Game.espn_event_id.is_(None))
            .filter(Game.completed == False)
            .all()
        )

        for game in games:
            away = game.away_team
            home = game.home_team
            if not away or not home:
                continue

            sport = (game.sport or away.sport or home.sport or "ncaa").lower()
            match = find_event_by_teams(away.team_name, home.team_name, sport)
            if not match or not match.get("event_id"):
                continue

            game.espn_event_id = str(match["event_id"])
            game.sport = sport
            game.source = "espn"
            kickoff = _parse_kickoff(match.get("kickoff"))
            if kickoff is not None:
                game.kickoff_time = kickoff

            _apply_team_data(away, match.get("away_team"), sport)
            _apply_team_data(home, match.get("home_team"), sport)
            repaired_ids.append(game.id)

        db.commit()
        return repaired_ids
    except Exception as error:
        db.rollback()
        print(f"repair_unlinked_games error: {error}")
        return []
    finally:
        db.close()


def run():
    repaired_ids = repair_unlinked_games()

    db = SessionLocal()
    try:
        linked = [
            (game.id, (game.sport or "ncaa").lower())
            for game in db.query(Game).filter(Game.espn_event_id.isnot(None)).all()
        ]
    finally:
        db.close()

    updated_count = 0
    for game_id, sport in linked:
        if update_game_from_espn(game_id, sport):
            updated_count += 1

    if repaired_ids:
        print(f"Repaired ESPN links for {len(repaired_ids)} game(s): {repaired_ids}")
    return updated_count


if __name__ == "__main__":
    updated = run()
    print(f"Updated {updated} games.")
