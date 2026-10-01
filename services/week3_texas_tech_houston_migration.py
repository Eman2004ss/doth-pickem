"""Idempotent restoration of the Week 3 Texas Tech-Houston game."""

from database.db import SessionLocal
from database.models import Game, Pick, Team, User, Week


def _get_or_create_team(db, name, abbreviation):
    team = db.query(Team).filter(Team.team_name == name).first()
    if team:
        return team

    team = Team(
        team_name=name,
        abbreviation=abbreviation,
        conference="BIG12",
        sport="ncaa",
        source="manual",
    )
    db.add(team)
    db.flush()
    return team


def run():
    db = SessionLocal()
    week_id = None
    changed = False

    try:
        week = db.query(Week).filter(Week.week_number == 3).with_for_update().first()
        if not week:
            print("Week 3 not found; skipping Texas Tech-Houston restore.")
            return False
        week_id = week.id

        texas_tech = _get_or_create_team(db, "Texas Tech Red Raiders", "TTU")
        houston = _get_or_create_team(db, "Houston Cougars", "HOU")

        game = (
            db.query(Game)
            .filter(
                Game.week_id == week.id,
                Game.home_team_id == texas_tech.id,
                Game.away_team_id == houston.id,
                Game.sport == "ncaa",
            )
            .first()
        )

        if not game:
            last_game = (
                db.query(Game)
                .filter(Game.week_id == week.id)
                .order_by(Game.game_number.desc(), Game.id.desc())
                .first()
            )

            game = Game(
                week_id=week.id,
                game_number=(last_game.game_number + 1) if last_game else 1,
                tier="A",
                sport="ncaa",
                source="manual",
                locked=True,
                home_team_id=texas_tech.id,
                away_team_id=houston.id,
                home_score=28,
                away_score=26,
                game_status="Final",
                winner_team_id=texas_tech.id,
                completed=True,
            )
            db.add(game)
            db.flush()
            changed = True
        else:
            requested_game_values = {
                "tier": "A",
                "locked": True,
                "home_score": 28,
                "away_score": 26,
                "game_status": "Final",
                "winner_team_id": texas_tech.id,
                "completed": True,
            }
            for field, value in requested_game_values.items():
                if getattr(game, field) != value:
                    setattr(game, field, value)
                    changed = True

        requested_picks = {
            "Hawes": (texas_tech.id, True, 5),
            "Jimbo": (texas_tech.id, True, 5),
            "Coleman": (houston.id, False, 0),
        }

        for username, (team_id, correct, points) in requested_picks.items():
            user = db.query(User).filter(User.username == username).first()
            if not user:
                print(f"Week 3 restore warning: user {username!r} not found.")
                continue

            pick = db.query(Pick).filter(
                Pick.user_id == user.id,
                Pick.game_id == game.id,
            ).first()

            if not pick:
                db.add(
                    Pick(
                        user_id=user.id,
                        game_id=game.id,
                        selected_team_id=team_id,
                        locked=True,
                        is_correct=correct,
                        points_awarded=points,
                    )
                )
                changed = True
                continue

            requested_pick_values = {
                "selected_team_id": team_id,
                "locked": True,
                "is_correct": correct,
                "points_awarded": points,
            }
            for field, value in requested_pick_values.items():
                if getattr(pick, field) != value:
                    setattr(pick, field, value)
                    changed = True

        db.commit()

    except Exception as error:
        db.rollback()
        print(f"Week 3 Texas Tech-Houston restore failed: {error}")
        return False
    finally:
        db.close()

    if changed and week_id is not None:
        from tasks.calculate_results import calculate_week_winner, sync_weekly_win_counts
        from services.leaderboard_service import update_all_leaderboards

        calculate_week_winner(week_id)
        sync_weekly_win_counts()
        update_all_leaderboards()

    return changed
