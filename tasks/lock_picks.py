from services.locking_service import (
    lock_expired_games
)


def run():

    locked_games = lock_expired_games()

    return len(locked_games)


if __name__ == "__main__":

    locked_count = run()

    print(
        f"Locked picks for {locked_count} games."
    )
