from database.db import SessionLocal
from database.extra_models import PlayoffGame, PlayoffPick


BRACKETS = {
    "cfb": [
        ("first_round", "First Round", 4),
        ("quarterfinal", "Quarterfinal", 4),
        ("semifinal", "Semifinal", 2),
        ("championship", "Championship", 1),
    ],
    "nfl": [
        ("wild_card", "Wild Card", 6),
        ("divisional", "Divisional", 4),
        ("conference", "Conference Championship", 2),
        ("super_bowl", "Super Bowl", 1),
    ],
}


def ensure_bracket_seeded(sport):
    """Create TBD placeholder rows for every slot that doesn't exist yet."""
    db = SessionLocal()
    try:
        for round_key, _label, count in BRACKETS.get(sport, []):
            for slot in range(1, count + 1):
                existing = (
                    db.query(PlayoffGame)
                    .filter(PlayoffGame.sport == sport)
                    .filter(PlayoffGame.round_key == round_key)
                    .filter(PlayoffGame.slot == slot)
                    .first()
                )
                if not existing:
                    db.add(
                        PlayoffGame(
                            sport=sport,
                            round_key=round_key,
                            slot=slot,
                            team1="TBD",
                            team2="TBD",
                        )
                    )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_bracket(sport):
    """Return the bracket as a list of rounds, each with its games in slot order."""
    ensure_bracket_seeded(sport)
    db = SessionLocal()
    try:
        rows = (
            db.query(PlayoffGame)
            .filter(PlayoffGame.sport == sport)
            .order_by(PlayoffGame.round_key, PlayoffGame.slot)
            .all()
        )
        by_round = {}
        for row in rows:
            by_round.setdefault(row.round_key, {})[row.slot] = row

        bracket = []
        for round_key, label, count in BRACKETS.get(sport, []):
            games = []
            for slot in range(1, count + 1):
                row = by_round.get(round_key, {}).get(slot)
                games.append({
                    "slot": slot,
                    "team1": row.team1 if row else "TBD",
                    "team2": row.team2 if row else "TBD",
                    "winner": row.winner if row else None,
                })
            bracket.append({"round_key": round_key, "label": label, "games": games})
        return bracket
    finally:
        db.close()


def save_playoff_game(sport, round_key, slot, team1, team2, winner=None):
    db = SessionLocal()
    try:
        row = (
            db.query(PlayoffGame)
            .filter(PlayoffGame.sport == sport)
            .filter(PlayoffGame.round_key == round_key)
            .filter(PlayoffGame.slot == slot)
            .first()
        )
        team1 = (team1 or "TBD").strip() or "TBD"
        team2 = (team2 or "TBD").strip() or "TBD"
        winner = (winner or "").strip() or None
        if not row:
            row = PlayoffGame(sport=sport, round_key=round_key, slot=slot)
            db.add(row)
        row.team1 = team1
        row.team2 = team2
        row.winner = winner
        db.commit()
        return True, "Saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save: {error}"
    finally:
        db.close()


def get_user_playoff_picks(user_id, sport):
    """Return {(round_key, slot): selection} for this user's picks in a sport."""
    db = SessionLocal()
    try:
        rows = (
            db.query(PlayoffPick)
            .filter(PlayoffPick.user_id == user_id)
            .filter(PlayoffPick.sport == sport)
            .all()
        )
        return {(row.round_key, row.slot): row.selection for row in rows}
    finally:
        db.close()


def save_playoff_pick(user_id, sport, round_key, slot, selection):
    if not selection or selection.strip().upper() == "TBD":
        return False, "That team isn't set yet."

    db = SessionLocal()
    try:
        row = (
            db.query(PlayoffPick)
            .filter(PlayoffPick.user_id == user_id)
            .filter(PlayoffPick.sport == sport)
            .filter(PlayoffPick.round_key == round_key)
            .filter(PlayoffPick.slot == slot)
            .first()
        )
        if not row:
            row = PlayoffPick(
                user_id=user_id,
                sport=sport,
                round_key=round_key,
                slot=slot,
            )
            db.add(row)
        row.selection = selection.strip()
        db.commit()
        return True, "Pick saved."
    except Exception as error:
        db.rollback()
        return False, f"Unable to save pick: {error}"
    finally:
        db.close()
