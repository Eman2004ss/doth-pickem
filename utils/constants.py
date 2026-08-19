# =====================================================
# USER SETTINGS
# =====================================================

ADMIN_USERNAME = "Hawes"

DEFAULT_USERS = [
    "Hawes",
    "Clong",
    "Jimbo"
]


# =====================================================
# SCORING
# =====================================================

TIER_POINTS = {
    "S": 6,
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
    "E": 1
}

WEEKLY_WIN_BONUS = 5


# =====================================================
# GAME SETTINGS
# =====================================================

GAMES_PER_WEEK = 5

MAX_USERS = 3


# =====================================================
# GAME STATUS
# =====================================================

GAME_STATUS_SCHEDULED = "Scheduled"

GAME_STATUS_PRE_GAME = "Pre-Game"

GAME_STATUS_IN_PROGRESS = "In Progress"

GAME_STATUS_HALFTIME = "Halftime"

GAME_STATUS_FINAL = "Final"


# =====================================================
# ESPN
# =====================================================

ESPN_NCAA_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "football/college-football/scoreboard"
)

ESPN_NFL_SCOREBOARD_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "football/nfl/scoreboard"
)


# =====================================================
# COLORS
# =====================================================

CORRECT_PICK_COLOR = "#22c55e"

INCORRECT_PICK_COLOR = "#ef4444"

PRIMARY_BLUE = "#2563eb"

BACKGROUND_COLOR = "#0f1115"

CARD_COLOR = "#181b20"


# =====================================================
# TIER ORDER
# =====================================================

VALID_TIERS = [
    "S",
    "A",
    "B",
    "C",
    "D",
    "E"
]