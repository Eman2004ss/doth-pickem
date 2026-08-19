from apscheduler.schedulers.background import BackgroundScheduler

from nicegui import ui, app

from pages.login import login_page
from pages.home import home_page
from pages.admin import admin_page
from pages.weekly_picks import weekly_picks_page
from pages.everyone_picks import everyone_picks_page
from pages.live_results import live_results_page
from pages.leaderboard import leaderboard_page
from pages.rules import rules_page

from tasks.update_games import run as update_games
from tasks.update_scores import run as update_scores
from tasks.lock_picks import run as lock_picks
from tasks.calculate_results import run as calculate_results

from services.leaderboard_service import (
    update_all_leaderboards
)


app.add_static_files(
    "/assets",
    "assets"
)


scheduler = BackgroundScheduler()


def scheduled_update_games():
    try:
        update_games()
    except Exception as e:
        print(f"update_games error: {e}")


def scheduled_update_scores():
    try:
        update_scores()
    except Exception as e:
        print(f"update_scores error: {e}")


def scheduled_lock_picks():
    try:
        lock_picks()
    except Exception as e:
        print(f"lock_picks error: {e}")


def scheduled_calculate_results():
    try:
        calculate_results()
    except Exception as e:
        print(f"calculate_results error: {e}")


def scheduled_leaderboard_update():
    try:
        update_all_leaderboards()
    except Exception as e:
        print(f"leaderboard update error: {e}")


scheduler.add_job(
    scheduled_update_games,
    "interval",
    minutes=1
)

scheduler.add_job(
    scheduled_update_scores,
    "interval",
    minutes=1
)

scheduler.add_job(
    scheduled_lock_picks,
    "interval",
    minutes=1
)

scheduler.add_job(
    scheduled_calculate_results,
    "interval",
    minutes=1
)

scheduler.add_job(
    scheduled_leaderboard_update,
    "interval",
    minutes=1
)

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


import os

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
    storage_secret="DothPickSecretKey",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
)