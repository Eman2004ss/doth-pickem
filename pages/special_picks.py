from datetime import datetime, timezone
import re

from nicegui import app, ui

from services.leaderboard_service import update_all_leaderboards
from services.special_pick_service import (
    CFB_CONFERENCES,
    NFL_DIVISIONS,
    get_cfb_conference_teams,
    get_nfl_teams,
    get_special_lock_time,
    get_special_pick,
    get_special_picks,
    get_team_names,
    is_special_locked,
    save_conference_pick,
    save_ranked_picks,
    save_special_pick,
    set_special_lock,
    get_all_fbs_teams,
)
from services.special_scoring_service import get_outcome, score_all_special_picks, set_outcome
from utils.ui_helpers import dark_page_container


CARD = "background-color:#151515;color:white;border:1px solid #333;border-radius:14px;padding:18px;margin-top:12px;"
PERIOD_LABELS = {"preseason": "Preseason", "midseason": "Midseason", "postseason": "Postseason"}
STAGE_OPTIONS_CFP = {
    "dnq": "Did Not Qualify",
    "round1": "Round 1",
    "quarterfinal": "Quarterfinal",
    "semifinal": "Semifinal",
    "championship": "Championship Game",
    "champion": "Champion",
}
STAGE_OPTIONS_NFL = {
    "dnq": "Did Not Qualify",
    "wild_card": "Wild Card",
    "divisional": "Divisional",
    "conference": "Conference Championship",
    "super_bowl": "Super Bowl",
    "champion": "Champion",
}


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def _lock_text(category, period):
    lock_at = get_special_lock_time(category, period)
    locked = is_special_locked(category, period)
    if lock_at:
        when = lock_at.strftime("%Y-%m-%d %H:%M UTC")
        return ("LOCKED" if locked else f"Locks {when}"), locked
    return ("No automatic lock found - admin should set an override", locked)


def _notify(result):
    success, message = result
    ui.notify(message, color="positive" if success else "negative")


def special_picks_page():
    with dark_page_container():
        with ui.row().classes("w-full items-center justify-between wrap"):
            ui.label("Special Picks").classes("text-h3").style("color:white;")
            with ui.row():
                ui.button("Weekly Picks", on_click=lambda: ui.navigate.to("/weekly-picks"))
                ui.button("Home", on_click=lambda: ui.navigate.to("/home"))

        user_id = app.storage.user.get("user_id")
        is_admin = bool(app.storage.user.get("is_admin", False))
        if not user_id:
            ui.label("Please log in first.").style("color:white;")
            return

        ui.label(
            "Long-range champion picks are stored separately from weekly games and are automatically added to the season leaderboard when results are entered."
        ).style("color:#d1d5db;")

        # ------------------------------------------------------------------
        # CFB conference champions
        # ------------------------------------------------------------------
        with ui.card().classes("w-full").style(CARD):
            ui.label("CFB Conference Champions").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Choose a different team for each preseason, midseason and postseason guess within a conference.").style("color:#d1d5db;")
            cfb_period = ui.select(
                options={"preseason": "Preseason", "midseason": "Midseason", "postseason": "Postseason"},
                value="preseason",
                label="Pick period",
            )
            cfb_container = ui.column().classes("w-full")

            def render_cfb():
                cfb_container.clear()
                period = cfb_period.value or "preseason"
                status, locked = _lock_text("cfb_conference", period)
                with cfb_container:
                    ui.label(status).style("color:#ef4444;font-weight:bold;" if locked else "color:#facc15;")
                    for conference in CFB_CONFERENCES:
                        current = get_special_pick(user_id, "cfb_conference", period, conference)
                        options = get_cfb_conference_teams(conference)
                        with ui.row().classes("w-full items-end wrap"):
                            select = ui.select(
                                options=options,
                                value=current.selection if current else None,
                                label=conference,
                                with_input=True,
                            ).style("min-width:300px;flex:1;")
                            button = ui.button(
                                f"Save {conference}",
                                on_click=lambda conference=conference, select=select, period=period: _notify(
                                    save_conference_pick(user_id, period, conference, select.value)
                                ),
                            )
                            if locked:
                                select.disable()
                                button.disable()

            cfb_period.on("update:model-value", lambda e: render_cfb())
            render_cfb()

        # ------------------------------------------------------------------
        # CFP preseason champion confidence picks
        # ------------------------------------------------------------------
        with ui.card().classes("w-full").style(CARD):
            ui.label("CFP Preseason Champion Picks").classes("text-h5").style("color:white;font-weight:bold;")
            status, locked = _lock_text("cfp_preseason", "preseason")
            ui.label(status).style("color:#ef4444;font-weight:bold;" if locked else "color:#facc15;")
            cfp_teams = get_all_fbs_teams()
            existing = {row.rank: row.selection for row in get_special_picks(user_id, "cfp_preseason", "preseason")}
            cfp_selects = []
            for rank in range(1, 4):
                select = ui.select(
                    options=cfp_teams,
                    value=existing.get(rank),
                    label=f"Rank {rank} {'(most confident)' if rank == 1 else ''}",
                    with_input=True,
                ).classes("w-full")
                cfp_selects.append(select)
                if locked:
                    select.disable()
            cfp_button = ui.button(
                "Save CFP Preseason Picks",
                on_click=lambda: _notify(
                    save_ranked_picks(user_id, "cfp_preseason", "preseason", [select.value for select in cfp_selects])
                ),
            )
            if locked:
                cfp_button.disable()

        # ------------------------------------------------------------------
        # NFL Super Bowl champion picks (preseason / midseason / postseason)
        # ------------------------------------------------------------------
        with ui.card().classes("w-full").style(CARD):
            ui.label("NFL Super Bowl Picks").classes("text-h5").style("color:white;font-weight:bold;")
            nfl_period = ui.select(
                options={"preseason": "Preseason", "midseason": "Midseason", "postseason": "Postseason"},
                value="preseason",
                label="Pick period",
            )
            nfl_container = ui.column().classes("w-full")

            def render_nfl():
                nfl_container.clear()
                period = nfl_period.value or "preseason"

                with nfl_container:
                    if period == "preseason":
                        ui.label(
                            "Rank four different teams. The four must contain exactly 2 AFC and 2 NFC teams."
                        ).style("color:#d1d5db;")
                        status, locked = _lock_text("nfl_preseason", "preseason")
                        ui.label(status).style("color:#ef4444;font-weight:bold;" if locked else "color:#facc15;")
                        nfl_teams = get_nfl_teams()
                        existing = {
                            row.rank: row.selection
                            for row in get_special_picks(user_id, "nfl_preseason", "preseason")
                        }
                        nfl_rank_selects = []
                        for rank in range(1, 5):
                            select = ui.select(
                                options=nfl_teams,
                                value=existing.get(rank),
                                label=f"Rank {rank}",
                                with_input=True,
                            ).classes("w-full")
                            nfl_rank_selects.append(select)
                            if locked:
                                select.disable()
                        nfl_pre_button = ui.button(
                            "Save NFL Preseason Picks",
                            on_click=lambda: _notify(
                                save_ranked_picks(
                                    user_id,
                                    "nfl_preseason",
                                    "preseason",
                                    [select.value for select in nfl_rank_selects],
                                )
                            ),
                        )
                        if locked:
                            nfl_pre_button.disable()
                    else:
                        status, locked = _lock_text("nfl_champion", period)
                        ui.label(status).style("color:#ef4444;font-weight:bold;" if locked else "color:#facc15;")
                        for conference in ("AFC", "NFC"):
                            current = get_special_pick(user_id, "nfl_champion", period, conference)
                            select = ui.select(
                                options=get_nfl_teams(conference),
                                value=current.selection if current else None,
                                label=f"{conference} guess",
                                with_input=True,
                            ).classes("w-full")
                            button = ui.button(
                                f"Save {conference}",
                                on_click=lambda select=select, conference=conference, period=period: _notify(
                                    save_special_pick(user_id, "nfl_champion", period, conference, select.value)
                                ),
                            )
                            if locked:
                                select.disable()
                                button.disable()

            nfl_period.on("update:model-value", lambda e: render_nfl())
            render_nfl()
        

        # ------------------------------------------------------------------
        # NFL division winners
        # ------------------------------------------------------------------
        with ui.card().classes("w-full").style(CARD):
            ui.label("NFL Preseason Division Champions").classes("text-h5").style("color:white;font-weight:bold;")
            ui.label("Each correct division winner is worth 4 points.").style("color:#d1d5db;")
            status, locked = _lock_text("nfl_division", "preseason")
            ui.label(status).style("color:#ef4444;font-weight:bold;" if locked else "color:#facc15;")
            for division, options in NFL_DIVISIONS.items():
                current = get_special_pick(user_id, "nfl_division", "preseason", division)
                with ui.row().classes("w-full items-end wrap"):
                    select = ui.select(
                        options=options,
                        value=current.selection if current else None,
                        label=division,
                    ).style("min-width:300px;flex:1;")
                    button = ui.button(
                        f"Save {division}",
                        on_click=lambda select=select, division=division: _notify(
                            save_special_pick(user_id, "nfl_division", "preseason", division, select.value)
                        ),
                    )
                    if locked:
                        select.disable()
                        button.disable()

        if is_admin:
            _render_admin_controls()


def _parse_utc(value):
    value = (value or "").strip()
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _render_admin_controls():
    with ui.card().classes("w-full").style(CARD + "border-left:6px solid #60a5fa;"):
        ui.label("Admin: Special Pick Locks").classes("text-h5").style("color:#60a5fa;font-weight:bold;")
        ui.label(
            "Preseason/midseason locks derive from the relevant first kickoff. Postseason locks use ESPN's conference-championship/playoff schedule. Enter an ISO UTC override whenever you want an exact custom cutoff."
        ).style("color:#d1d5db;")

        lock_keys = [
            ("cfb_conference", "preseason", "CFB conference preseason"),
            ("cfb_conference", "midseason", "CFB conference midseason"),
            ("cfb_conference", "postseason", "CFB conference postseason"),
            ("cfp_preseason", "preseason", "CFP preseason"),
            ("nfl_preseason", "preseason", "NFL preseason Super Bowl"),
            ("nfl_champion", "midseason", "NFL midseason Super Bowl"),
            ("nfl_champion", "postseason", "NFL postseason Super Bowl"),
            ("nfl_division", "preseason", "NFL division preseason"),
        ]
        for category, period, label in lock_keys:
            effective = get_special_lock_time(category, period)
            with ui.row().classes("w-full items-end wrap"):
                ui.label(label).style("color:white;min-width:240px;font-weight:bold;")
                override = ui.input(
                    label="UTC override (YYYY-MM-DD HH:MM)",
                    placeholder=effective.strftime("%Y-%m-%d %H:%M") if effective else "",
                ).style("min-width:280px;flex:1;")
                force = ui.checkbox("Force locked")

                def save_lock(category=category, period=period, override=override, force=force):
                    try:
                        parsed = _parse_utc(override.value)
                    except Exception:
                        ui.notify("Use YYYY-MM-DD HH:MM (UTC).", color="negative")
                        return
                    success = set_special_lock(category, period, parsed, force.value)
                    ui.notify("Lock saved." if success else "Unable to save lock.", color="positive" if success else "negative")

                ui.button("Save Lock", on_click=save_lock)

    with ui.card().classes("w-full").style(CARD + "border-left:6px solid #22c55e;"):
        ui.label("Admin: Enter Special Pick Results").classes("text-h5").style("color:#22c55e;font-weight:bold;")
        ui.label("Saving results recalculates special-pick points immediately.").style("color:#d1d5db;")

        ncaa_teams = get_team_names("ncaa")
        ui.label("CFB Conference Champions").classes("text-h6").style("color:white;")
        for conference in CFB_CONFERENCES:
            current = get_outcome("cfb_conference", conference)
            select = ui.select(
                options=get_cfb_conference_teams(conference) or ncaa_teams,
                value=current.result if current else None,
                label=f"Actual {conference} champion",
                with_input=True,
            ).classes("w-full")

            def save_conf(conference=conference, select=select):
                if not select.value:
                    ui.notify("Choose the champion first.", color="negative")
                    return
                set_outcome("cfb_conference", conference, select.value)
                score_all_special_picks()
                update_all_leaderboards()
                ui.notify(f"{conference} result saved.", color="positive")

            ui.button(f"Save {conference} Result", on_click=save_conf)

        ui.separator().style("background:#333;")
        ui.label("CFP Team Outcomes").classes("text-h6").style("color:white;")
        cfp_teams = sorted({row.selection for row in get_special_picks(category="cfp_preseason")})
        for team in cfp_teams:
            current = get_outcome("cfp_preseason", _norm(team))
            stage = ui.select(
                options=STAGE_OPTIONS_CFP,
                value=current.result if current else None,
                label=f"{team} final CFP result",
            ).classes("w-full")

            def save_cfp(team=team, stage=stage):
                if not stage.value:
                    return ui.notify("Choose a result stage.", color="negative")
                set_outcome("cfp_preseason", _norm(team), stage.value)
                score_all_special_picks()
                update_all_leaderboards()
                ui.notify(f"{team} result saved.", color="positive")

            ui.button(f"Save {team}", on_click=save_cfp)

        ui.separator().style("background:#333;")
        ui.label("NFL Team Outcomes").classes("text-h6").style("color:white;")
        nfl_rows = get_special_picks(category="nfl_preseason") + get_special_picks(category="nfl_champion")
        nfl_teams = sorted({row.selection for row in nfl_rows})
        for team in nfl_teams:
            current = get_outcome("nfl_team", _norm(team))
            with ui.row().classes("w-full items-end wrap"):
                stage = ui.select(
                    options=STAGE_OPTIONS_NFL,
                    value=current.result if current else None,
                    label=f"{team} final result",
                ).style("min-width:300px;flex:1;")
                bye = ui.checkbox("Had first-round bye", value=bool(current.had_bye) if current else False)

                def save_nfl(team=team, stage=stage, bye=bye):
                    if not stage.value:
                        return ui.notify("Choose a result stage.", color="negative")
                    set_outcome("nfl_team", _norm(team), stage.value, bye.value)
                    score_all_special_picks()
                    update_all_leaderboards()
                    ui.notify(f"{team} result saved.", color="positive")

                ui.button("Save", on_click=save_nfl)

        ui.separator().style("background:#333;")
        ui.label("NFL Division Champions").classes("text-h6").style("color:white;")
        for division, options in NFL_DIVISIONS.items():
            current = get_outcome("nfl_division", division)
            with ui.row().classes("w-full items-end wrap"):
                select = ui.select(options=options, value=current.result if current else None, label=division).style("min-width:300px;flex:1;")

                def save_division(division=division, select=select):
                    if not select.value:
                        return ui.notify("Choose a team first.", color="negative")
                    set_outcome("nfl_division", division, select.value)
                    score_all_special_picks()
                    update_all_leaderboards()
                    ui.notify(f"{division} result saved.", color="positive")

                ui.button("Save Result", on_click=save_division)
