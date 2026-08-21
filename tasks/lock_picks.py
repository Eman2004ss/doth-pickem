from services.locking_service import lock_expired_games
from services.special_pick_service import lock_expired_special_picks
from services.tiebreaker_service import lock_expired_tiebreakers


def run():
    locked_games = lock_expired_games()
    tiebreakers = lock_expired_tiebreakers()
    specials = lock_expired_special_picks()
    return len(locked_games) + tiebreakers + specials


if __name__ == "__main__":
    locked_count = run()
    print(f"Locked {locked_count} game, tiebreaker, or special-pick records.")
