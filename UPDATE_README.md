# DothPick 2026 scoring + special picks update

This ZIP is an **overlay update** for the current `Eman2004ss/doth-pickem` repository.  It contains only files that are new or intentionally replaced.  Copy the contents over the existing repository; do **not** delete untouched folders such as `assets/`, `data/`, or existing database files.

## What changed

- ESPN matchup lookup now searches the season schedule instead of only today's/default scoreboard.
- Linked ESPN event updates use the event-summary endpoint so future-linked games still update when their game day arrives.
- The background updater now retries previously unlinked games, so a board saved before ESPN exposed the event can repair itself automatically.
- Tier scoring is S=6, A=5, B=4, C=3, D=2, F=1.
- Existing database rows with tier E are automatically renamed to F at startup; the value stays 1 point.
- Every weekly board has a Game 1 total-points tiebreaker that locks at Game 1 kickoff.
- Week 13 is Rivalry Week: all five games are 3 points, outright weekly bonus is 10, tied leaders use 7/3 tiebreaker payout.
- Weekly bonus points are now included when the leaderboard recalculates (the prior implementation could overwrite them).
- New `/special-picks` page for:
  - CFB conference champions: preseason, midseason, postseason
  - CFP preseason champion rankings
  - NFL preseason Super Bowl rankings (exactly 2 AFC + 2 NFC)
  - NFL midseason and postseason AFC/NFC Super Bowl picks
  - NFL preseason division champions
- Special picks lock automatically at the rule-based cutoff and admins can override/force lock times.
- Admin result entry on the Special Picks page scores the long-range picks with the point tables in the rules.
- Updated Rules page uses F instead of E and describes the automated scoring.

## Database behavior

No existing production table is destructively changed. New tables are created automatically by SQLAlchemy on startup:

- `tiebreaker_picks`
- `special_picks`
- `special_outcomes`
- `special_locks`
- `special_bonuses`

The only existing-data migration is `games.tier = 'E'` -> `'F'`.

## Files to overlay

- `app.py`
- `utils/constants.py`
- `database/extra_models.py` (new)
- `services/espn_compat.py` (new)
- `services/startup_migrations.py` (new)
- `services/tiebreaker_service.py` (new)
- `services/special_pick_service.py` (new)
- `services/special_scoring_service.py` (new)
- `services/scoring_service.py`
- `tasks/calculate_results.py`
- `tasks/lock_picks.py`
- `tasks/update_games.py`
- `pages/home.py`
- `pages/weekly_picks.py`
- `pages/special_picks.py` (new)
- `pages/rules_v2.py` (new)

## First deployment check

After deployment, the one-minute background updater will retry games that were previously saved without an ESPN event ID. You can also open Admin and save/re-save the week to force an immediate lookup. Matchups should show `ESPN linked`/`ESPN match found` for games ESPN has published. Then open Weekly Picks and verify the tiebreaker card. Open Special Picks and verify the long-range sections. Admin accounts will also see lock overrides and result-entry controls at the bottom of Special Picks.
