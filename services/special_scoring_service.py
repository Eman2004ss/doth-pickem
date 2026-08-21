import re

from database.db import SessionLocal
from database.models import User
from database.extra_models import SpecialBonus, SpecialOutcome, SpecialPick


CFB_CONFERENCE_POINTS = {
    "preseason": {"Big Ten": 9, "SEC": 9, "ACC": 7, "Big 12": 7},
    "midseason": {"Big Ten": 7, "SEC": 7, "ACC": 5, "Big 12": 5},
    "postseason": {"Big Ten": 5, "SEC": 5, "ACC": 4, "Big 12": 4},
}

CFP_PRESEASON_POINTS = {
    1: {"dnq": -3, "round1": 3, "quarterfinal": 6, "semifinal": 9, "championship": 12, "champion": 20},
    2: {"dnq": -2, "round1": 2, "quarterfinal": 4, "semifinal": 6, "championship": 8, "champion": 15},
    3: {"dnq": -1, "round1": 1, "quarterfinal": 2, "semifinal": 4, "championship": 6, "champion": 10},
}

NFL_PRESEASON_POINTS = {
    1: {"dnq": -5, "wild_card": 4, "divisional": 8, "conference": 12, "super_bowl": 15, "champion": 20},
    2: {"dnq": -4, "wild_card": 3, "divisional": 6, "conference": 9, "super_bowl": 12, "champion": 18},
    3: {"dnq": -3, "wild_card": 2, "divisional": 4, "conference": 6, "super_bowl": 8, "champion": 12},
    4: {"dnq": -2, "wild_card": 1, "divisional": 3, "conference": 5, "super_bowl": 7, "champion": 10},
}

NFL_MIDSEASON_POINTS = {
    "dnq": (-10, -10),
    "wild_card": (0, -5),
    "divisional": (3, 3),
    "conference": (6, 6),
    "super_bowl": (9, 9),
    "champion": (15, 15),
}

NFL_POSTSEASON_POINTS = {
    "dnq": (-8, -8),
    "wild_card": (-8, -8),
    "divisional": (0, -8),
    "conference": (3, 3),
    "super_bowl": (6, 6),
    "champion": (12, 12),
}

VALID_STAGES = ["dnq", "round1", "wild_card", "quarterfinal", "divisional", "semifinal", "conference", "championship", "super_bowl", "champion"]


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def set_outcome(category, key, result, had_bye=False):
    db = SessionLocal()
    try:
        row = (
            db.query(SpecialOutcome)
            .filter(SpecialOutcome.category == category)
            .filter(SpecialOutcome.key == key)
            .first()
        )
        if not row:
            row = SpecialOutcome(category=category, key=key, result=result, had_bye=bool(had_bye))
            db.add(row)
        else:
            row.result = result
            row.had_bye = bool(had_bye)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_outcome(category, key):
    db = SessionLocal()
    try:
        return (
            db.query(SpecialOutcome)
            .filter(SpecialOutcome.category == category)
            .filter(SpecialOutcome.key == key)
            .first()
        )
    finally:
        db.close()


def _find_team_outcome(db, category, team_name):
    key = _norm(team_name)
    return (
        db.query(SpecialOutcome)
        .filter(SpecialOutcome.category == category)
        .filter(SpecialOutcome.key == key)
        .first()
    )


def _score_pick(db, pick):
    if pick.category == "cfb_conference":
        outcome = (
            db.query(SpecialOutcome)
            .filter(SpecialOutcome.category == "cfb_conference")
            .filter(SpecialOutcome.key == pick.slot)
            .first()
        )
        if not outcome:
            return 0
        if _norm(pick.selection) != _norm(outcome.result):
            return 0
        return CFB_CONFERENCE_POINTS.get(pick.period, {}).get(pick.slot, 0)

    if pick.category == "cfp_preseason":
        outcome = _find_team_outcome(db, "cfp_preseason", pick.selection)
        if not outcome:
            return 0
        rank = int(pick.rank or 0)
        return CFP_PRESEASON_POINTS.get(rank, {}).get(outcome.result, 0)

    if pick.category == "nfl_preseason":
        outcome = _find_team_outcome(db, "nfl_team", pick.selection)
        if not outcome:
            return 0
        rank = int(pick.rank or 0)
        return NFL_PRESEASON_POINTS.get(rank, {}).get(outcome.result, 0)

    if pick.category == "nfl_champion":
        outcome = _find_team_outcome(db, "nfl_team", pick.selection)
        if not outcome:
            return 0
        table = NFL_MIDSEASON_POINTS if pick.period == "midseason" else NFL_POSTSEASON_POINTS
        no_bye, with_bye = table.get(outcome.result, (0, 0))
        return with_bye if outcome.had_bye else no_bye

    if pick.category == "nfl_division":
        outcome = (
            db.query(SpecialOutcome)
            .filter(SpecialOutcome.category == "nfl_division")
            .filter(SpecialOutcome.key == pick.slot)
            .first()
        )
        if not outcome:
            return 0
        return 4 if _norm(pick.selection) == _norm(outcome.result) else 0

    return 0


def score_all_special_picks():
    db = SessionLocal()
    try:
        picks = db.query(SpecialPick).all()
        for pick in picks:
            pick.points_awarded = int(_score_pick(db, pick))
        db.commit()
    except Exception as error:
        db.rollback()
        print(f"special scoring error: {error}")
    finally:
        db.close()
    recalculate_conference_bonus()


def recalculate_conference_bonus():
    """Award the rules' 10-point CFB conference-prediction pool bonus."""
    db = SessionLocal()
    try:
        db.query(SpecialBonus).filter(SpecialBonus.category == "cfb_conference").delete(synchronize_session=False)

        required = {"Big Ten", "SEC", "ACC", "Big 12"}
        outcomes = (
            db.query(SpecialOutcome)
            .filter(SpecialOutcome.category == "cfb_conference")
            .all()
        )
        if not required.issubset({row.key for row in outcomes}):
            db.commit()
            return

        # Only users who actually entered at least one CFB conference pick
        # are eligible for this prediction-pool bonus. Without this filter a
        # user with no entries could share the bonus when every submitted pick
        # happened to score zero.
        user_ids = [
            row[0]
            for row in db.query(SpecialPick.user_id)
            .filter(SpecialPick.category == "cfb_conference")
            .distinct()
            .all()
        ]
        totals = []
        for user_id in user_ids:
            total = sum(
                int(row.points_awarded or 0)
                for row in db.query(SpecialPick)
                .filter(SpecialPick.user_id == user_id)
                .filter(SpecialPick.category == "cfb_conference")
                .all()
            )
            totals.append((user_id, total))
        if not totals:
            db.commit()
            return
        best = max(total for _, total in totals)
        for user_id, total in totals:
            if total == best:
                db.add(SpecialBonus(
                    user_id=user_id,
                    category="cfb_conference",
                    bonus_key="overall_prediction_winner",
                    points=10,
                ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_special_total(user_id):
    db = SessionLocal()
    try:
        pick_points = sum(
            int(row.points_awarded or 0)
            for row in db.query(SpecialPick).filter(SpecialPick.user_id == user_id).all()
        )
        bonus_points = sum(
            int(row.points or 0)
            for row in db.query(SpecialBonus).filter(SpecialBonus.user_id == user_id).all()
        )
        return pick_points + bonus_points
    finally:
        db.close()
