import os

from apscheduler.schedulers.background import BackgroundScheduler
from nicegui import app, ui

# Register the additive tables before create_database() calls metadata.create_all.
import database.extra_models  # noqa: F401

# Patch ESPN schedule lookup before admin/tasks import functions from the legacy
# ESPN module.  This preserves the rest of the existing service unchanged.
from services.espn_compat import install_espn_patches
install_espn_patches()

from database.schema import create_database
create_database()

from services.startup_migrations import run_startup_migrations
run_startup_migrations()

from pages.admin import admin_page
from pages.everyone_picks import everyone_picks_page
from pages.home import home_page
from pages.leaderboard import leaderboard_page
from pages.live_results import live_results_page
from pages.login import login_page
from pages.playoffs import playoffs_page
from pages.rules_v2 import rules_page
from pages.special_picks import special_picks_page
from pages.weekly_picks import weekly_picks_page
from services.leaderboard_service import update_all_leaderboards
from tasks.calculate_results import run as calculate_results
from tasks.lock_picks import run as lock_picks
from tasks.update_games import run as update_games
from tasks.update_scores import run as update_scores


app.add_static_files("/assets", "assets")

scheduler = BackgroundScheduler()


def scheduled_update_games():
    try:
        update_games()
    except Exception as error:
        print(f"update_games error: {error}")


def scheduled_update_scores():
    try:
        update_scores()
    except Exception as error:
        print(f"update_scores error: {error}")


def scheduled_lock_picks():
    try:
        lock_picks()
    except Exception as error:
        print(f"lock_picks error: {error}")


def scheduled_calculate_results():
    try:
        calculate_results()
    except Exception as error:
        print(f"calculate_results error: {error}")


def scheduled_leaderboard_update():
    try:
        update_all_leaderboards()
    except Exception as error:
        print(f"leaderboard update error: {error}")


scheduler.add_job(scheduled_update_games, "interval", minutes=1)
scheduler.add_job(scheduled_update_scores, "interval", minutes=1)
scheduler.add_job(scheduled_lock_picks, "interval", minutes=1)
scheduler.add_job(scheduled_calculate_results, "interval", minutes=1)
scheduler.add_job(scheduled_leaderboard_update, "interval", minutes=1)
scheduler.start()


@ui.page("/")
def login():
    login_page()


@ui.page("/home")
def home():
    home_page()


@ui.page("/admin")
def admin():
    admin_page()


@ui.page("/weekly-picks")
def weekly_picks():
    weekly_picks_page()


@ui.page("/special-picks")
def special_picks():
    special_picks_page()


@ui.page("/everyone-picks")
def everyone_picks():
    everyone_picks_page()


@ui.page("/live-results")
def live_results():
    live_results_page()


@ui.page("/leaderboard")
def leaderboard():
    leaderboard_page()


@ui.page("/rules")
def rules():
    rules_page()


@ui.page("/playoffs")
def playoffs():
    playoffs_page()


ui.add_head_html(
    """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Doth Thou Knoweth Ball">
    """,
    shared=True,
)

ui.run(
    title="DothPick",
    favicon="/assets/favicon.png",
    reload=False,
    storage_secret=os.environ.get("STORAGE_SECRET", "DothPickSecretKey"),
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
)
