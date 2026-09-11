"""Admin game removal and standings repair in one database transaction."""
from database.db import SessionLocal
from database.models import Game, Pick, User, Leaderboard, WeeklyWinner
from database.extra_models import TiebreakerPick, SpecialPick, SpecialBonus
from utils.constants import (RIVALRY_WEEK_NUMBERS, RIVALRY_WEEK_WIN_BONUS,
    RIVALRY_WEEK_TIE_FIRST_BONUS, RIVALRY_WEEK_TIE_SECOND_BONUS, WEEKLY_WIN_BONUS)


def remove_game_as_admin(game_id, admin_user_id):
    db = SessionLocal()
    try:
        admin = db.get(User, admin_user_id) if admin_user_id else None
        if not admin or not admin.is_admin:
            return False, "Only administrators can remove games."
        game = db.query(Game).filter(Game.id == game_id).with_for_update().first()
        if not game:
            return False, "This game no longer exists."
        week_id, week_number = game.week_id, game.week.week_number
        first_game = db.query(Game).filter(Game.week_id == week_id).order_by(Game.game_number, Game.id).first()
        if first_game.id == game.id:
            db.query(TiebreakerPick).filter(TiebreakerPick.week_id == week_id).delete(synchronize_session=False)
        db.delete(game)  # ORM cascade removes its picks and awarded points.
        db.flush()
        db.query(WeeklyWinner).filter(WeeklyWinner.week_id == week_id).delete(synchronize_session=False)
        games = db.query(Game).filter(Game.week_id == week_id).order_by(Game.game_number, Game.id).all()
        users = db.query(User).all()
        if games and all(g.completed for g in games) and users:
            picks = db.query(Pick).join(Game).filter(Game.week_id == week_id).all()
            rivalry = week_number in RIVALRY_WEEK_NUMBERS
            values = {u.id: sum((int(bool(p.is_correct)) if rivalry else int(p.points_awarded or 0))
                               for p in picks if p.user_id == u.id) for u in users}
            best = max(values.values())
            tied = [uid for uid, value in values.items() if value == best]
            total = int(games[0].home_score or 0) + int(games[0].away_score or 0)
            guesses = db.query(TiebreakerPick).filter(TiebreakerPick.week_id == week_id).all()
            deviations = {p.user_id: abs(p.predicted_total - total) for p in guesses if p.user_id in tied}
            if not rivalry:
                if deviations:
                    closest = min(deviations.values())
                    tied = [uid for uid in tied if deviations.get(uid) == closest]
                payouts = [(uid, WEEKLY_WIN_BONUS) for uid in tied]
            elif len(tied) == 1:
                payouts = [(tied[0], RIVALRY_WEEK_WIN_BONUS)]
            else:
                ranked = sorted(tied, key=lambda uid: (deviations.get(uid, 10**9), uid))
                if len(ranked) == 2 and deviations.get(ranked[0], 10**9) == deviations.get(ranked[1], 10**9):
                    payouts = [(uid, 5) for uid in ranked]
                else:
                    payouts = [(ranked[0], RIVALRY_WEEK_TIE_FIRST_BONUS), (ranked[1], RIVALRY_WEEK_TIE_SECOND_BONUS)]
            for uid, bonus in payouts:
                if bonus > 0:
                    db.add(WeeklyWinner(week_id=week_id, user_id=uid, bonus_points=bonus))
        db.flush()
        rows = db.query(Leaderboard).all()
        for row in rows:
            picks = db.query(Pick).filter(Pick.user_id == row.user_id).all()
            bonuses = db.query(WeeklyWinner).filter(WeeklyWinner.user_id == row.user_id).all()
            special = db.query(SpecialPick).filter(SpecialPick.user_id == row.user_id).all()
            special_bonus = db.query(SpecialBonus).filter(SpecialBonus.user_id == row.user_id).all()
            row.total_picks = len(picks)
            row.correct_picks = sum(bool(p.is_correct) for p in picks)
            row.weekly_wins = sum(b.bonus_points >= 5 for b in bonuses)
            row.total_points = (sum(int(p.points_awarded or 0) for p in picks)
                                + sum(int(b.bonus_points or 0) for b in bonuses)
                                + sum(int(p.points_awarded or 0) for p in special)
                                + sum(int(b.points or 0) for b in special_bonus))
        for rank, row in enumerate(sorted(rows, key=lambda r: (-r.total_points, r.user_id)), 1):
            row.rank = rank
        db.commit()
        return True, "Game removed. Picks, points, weekly bonuses, and standings updated."
    except Exception:
        db.rollback()
        return False, "Unable to remove game. No changes were saved."
    finally:
        db.close()
