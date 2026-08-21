# Install the DothPick 2026 update

This ZIP is an overlay. It contains only the files that must be added or replaced. Do not delete the rest of the repository.

## Recommended: PowerShell / Git

1. Open PowerShell and go to your local repository:

```powershell
cd C:\path\to\doth-pickem
```

2. Make sure your current work is committed, then create a safety branch:

```powershell
git status
git add -A
git commit -m "Backup before 2026 scoring update"
git branch backup-before-2026-scoring-update
git push origin backup-before-2026-scoring-update
```

If `git commit` says there is nothing to commit, continue.

3. Make sure `main` is current:

```powershell
git switch main
git pull origin main
```

4. Extract the downloaded update ZIP directly into the repository root. If the ZIP is in Downloads:

```powershell
Expand-Archive -Path "$HOME\Downloads\DothPick_2026_Update.zip" -DestinationPath . -Force
```

The ZIP paths already include `pages\`, `services\`, `tasks\`, `database\`, and `utils\`. Do not create another nested project folder.

5. Verify what changed:

```powershell
git status
git diff --stat
```

6. Commit and push:

```powershell
git add -A
git commit -m "Add tiebreakers rivalry scoring and special picks"
git push origin main
```

7. Let the hosting service redeploy from `main`.

## First deployment checks

- Open Admin. Existing E-tier games should now display as F tier.
- Week 1 games that previously said `No ESPN match` should be retried automatically by the background updater. Saving the week again also performs an immediate lookup.
- Open Weekly Picks. Confirm a Game 1 total-points tiebreaker appears for the selected week.
- Open Week 13. Confirm the Rivalry Week banner appears and every game shows 3 points.
- Open Special Picks. Confirm the CFB/NFL preseason, midseason, and postseason sections are present.
- As admin, confirm automatic lock times appear and that the manual UTC override/force-lock controls are visible.

## Database notes

The startup code creates the new additive tables automatically. Existing pick/game/user tables are not deleted. The only migration of existing rows changes `games.tier` from `E` to `F`; its scoring value remains 1 point.

## Rule-edge decisions

The original rules did not define every possible exact tie. This implementation uses these deterministic fallbacks:

- Normal weekly winner: highest weekly points, then closest Game 1 total-points guess. If users remain exactly tied, they share the normal 5-point weekly-winner bonus.
- Rivalry Week: most correct picks wins. If tied, closest Game 1 total-points guess ranks the tied users. First receives 7 and second receives 3. If the top two have exactly the same tiebreaker error, the 10 available tie-bonus points are split 5/5.
- If 3+ users tie on Rivalry Week, the ordered fallback is 7/3/0 after the tiebreaker ranking.
- If the CFB conference-prediction pool finishes tied for the best score, all tied eligible leaders receive the 10-point pool bonus because the supplied rule set does not specify a second tiebreaker.

## Special-pick result entry

Locking is automatic. Long-range champion/division outcomes are entered by the admin on the Special Picks page when they become known; saving the outcome recalculates those picks and the leaderboard.
