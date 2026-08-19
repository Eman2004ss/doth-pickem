from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from utils.constants import TIER_POINTS
# =====================================================
# TIME FUNCTIONS
# =====================================================

def current_time():
    return datetime.utcnow()


def format_datetime(dt):

    if dt is None:
        return ""

    return dt.strftime("%m/%d/%Y %I:%M %p")


# =====================================================
# GAME FUNCTIONS
# =====================================================

def game_locked(kickoff_time):

    if kickoff_time is None:
        return False

    return current_time() >= kickoff_time


def determine_winner(
    home_team,
    away_team,
    home_score,
    away_score
):

    if home_score > away_score:
        return home_team

    if away_score > home_score:
        return away_team

    return None


# =====================================================
# PICK FUNCTIONS
# =====================================================

def pick_correct(
    selected_team,
    winning_team
):

    if winning_team is None:
        return None

    return selected_team == winning_team


def calculate_pick_points(
    selected_team,
    winning_team,
    tier
):

    if selected_team != winning_team:
        return 0

    return TIER_POINTS.get(tier, 0)


# =====================================================
# LEADERBOARD FUNCTIONS
# =====================================================

def calculate_accuracy(
    correct_picks,
    total_picks
):

    if total_picks == 0:
        return 0

    return round(
        (correct_picks / total_picks) * 100,
        1
    )


# =====================================================
# STRING FUNCTIONS
# =====================================================

def safe_string(value):

    if value is None:
        return ""

    return str(value).strip()


def safe_int(value):

    try:
        return int(value)

    except Exception:
        return 0


# =====================================================
# TEAM FUNCTIONS
# =====================================================

def matchup_name(
    away_team,
    home_team
):

    return f"{away_team} vs {home_team}"


def tier_display(
    away_team,
    home_team,
    tier
):

    return (
        f"{away_team} vs {home_team} ({tier})"
    )



from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def format_kickoff_et(kickoff_time):

    if not kickoff_time:
        return "TBD"

    dt = kickoff_time

    if isinstance(dt, str):

        try:

            dt = datetime.fromisoformat(
                dt.replace(
                    "Z",
                    "+00:00"
                )
            )

        except Exception:

            return str(kickoff_time)

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    eastern_time = dt.astimezone(
        ZoneInfo("America/New_York")
    )

    date_text = eastern_time.strftime(
        "%m/%d"
    )

    hour = eastern_time.strftime(
        "%I"
    ).lstrip("0")

    minute = eastern_time.strftime(
        "%M"
    )

    am_pm = eastern_time.strftime(
        "%p"
    ).lower()

    if am_pm == "am":

        am_pm = "a.m."

    else:

        am_pm = "p.m."

    return f"{date_text} at {hour}:{minute} {am_pm} ET"
