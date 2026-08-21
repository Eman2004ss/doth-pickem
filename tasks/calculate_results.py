from database.db import SessionLocal
from database.models import Game, Leaderboard, User, Week, WeeklyWinner
from services.leaderboard_service import update_all_leaderboards
from services.scoring_service import get_week_correct_picks, get_week_points, score_completed_game
from services.special_scoring_service import score_all_special_picks
from services.tiebreaker_service import actual_game_one_total, tiebreaker_deviation
from utils.constants import (
    RIVALRY_WEEK_NUMBERS,
    RIVALRY_WEEK_TIE_FIRST_BONUS,
    RIVALRY_WEEK_TIE_SECOND_BONUS,
    RIVALRY_WEEK_WIN_BONUS,
    WEEKLY_WIN_BONUS,
)


def score_completed_games():
    db = SessionLocal()
    try:
        games = db.query(Game).filter(Game.completed == True).all()
        return sum(1 for game in games if score_completed_game(game.id))
    finally:
        db.close()


def week_is_complete(week_id):
    db = SessionLocal()
    try:
        games = db.query(Game).filter(Game.week_id == week_id).all()
        return bool(games) and all(game.completed for game in games)
    finally:
        db.close()


def _resolve_regular_tie(user_ids, week_id):
    """Use Game 1 total-points prediction; preserve a true unresolved tie."""
    deviations = {uid: tiebreaker_deviation(uid, week_id) for uid in user_ids}
    available = {uid: dev for uid, dev in deviations.items() if dev is not None}
    if not available:
        return user_ids
    best = min(available.values())
    return [uid for uid, dev in available.items() if dev == best]


def _rivalry_payouts(user_ids, week_id):
    """Rivalry: 10 outright; tied leaders are ranked 7/3 by Game 1 tiebreaker."""
    if len(user_ids) == 1:
        return [(user_ids[0], RIVALRY_WEEK_WIN_BONUS)]

    # Missing tiebreakers rank behind submitted ones.  A three-way tie is
    # handled as 7/3/0; the published two-player 7/3 rule is preserved exactly.
    ranked = []
    for uid in user_ids:
        deviation = tiebreaker_deviation(uid, week_id)
        ranked.append((uid, deviation if deviation is not None else 10**9))
    ranked.sort(key=lambda item: (item[1], item[0]))

    if len(ranked) == 2 and ranked[0][1] == ranked[1][1]:
        # If both guesses are equally close, split the published 10 bonus 5/5.
        return [(ranked[0][0], 5), (ranked[1][0], 5)]

    payouts = [(ranked[0][0], RIVALRY_WEEK_TIE_FIRST_BONUS)]
    if len(ranked) >= 2:
        payouts.append((ranked[1][0], RIVALRY_WEEK_TIE_SECOND_BONUS))
    return payouts


def calculate_week_winner(week_id):
    db = SessionLocal()
    try:
        if not week_is_complete(week_id):
            return None
        week = db.query(Week).filter(Week.id == week_id).first()
        users = db.query(User).all()
        if not week or not users:
            return None

        # Recalculate instead of permanently trusting an earlier result. This
        # makes corrected ESPN finals/tiebreakers safe.
        db.query(WeeklyWinner).filter(WeeklyWinner.week_id == week_id).delete(synchronize_session=False)

        if week.week_number in RIVALRY_WEEK_NUMBERS:
            values = [(user.id, get_week_correct_picks(user.id, week_id)) for user in users]
            best = max(value for _, value in values)
            tied = [uid for uid, value in values if value == best]
            payouts = _rivalry_payouts(tied, week_id)
        else:
            values = [(user.id, get_week_points(user.id, week_id)) for user in users]
            best = max(value for _, value in values)
            tied = [uid for uid, value in values if value == best]
            winners = _resolve_regular_tie(tied, week_id)
            payouts = [(uid, WEEKLY_WIN_BONUS) for uid in winners]

        created = []
        for user_id, bonus in payouts:
            if bonus <= 0:
                continue
            row = WeeklyWinner(week_id=week_id, user_id=user_id, bonus_points=int(bonus))
            db.add(row)
            created.append(row)
        db.commit()
        return created
    except Exception as error:
        db.rollback()
        print(f"weekly winner error: {error}")
        return None
    finally:
        db.close()


def calculate_all_week_winners():
    db = SessionLocal()
    try:
        weeks = db.query(Week).all()
    finally:
        db.close()
    count = 0
    for week in weeks:
        if calculate_week_winner(week.id) is not None:
            count += 1
    sync_weekly_win_counts()
    return count


def sync_weekly_win_counts():
    """Count full/shared winners, not the 3-point rivalry runner-up."""
    db = SessionLocal()
    try:
        for row in db.query(Leaderboard).all():
            row.weekly_wins = (
                db.query(WeeklyWinner)
                .filter(WeeklyWinner.user_id == row.user_id)
                .filter(WeeklyWinner.bonus_points >= 5)
                .count()
            )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def run():
    scored_games = score_completed_games()
    calculate_all_week_winners()
    score_all_special_picks()
    update_all_leaderboards()
    return scored_games


if __name__ == "__main__":
    total_scored = run()
    print(f"Scored {total_scored} completed games.")
