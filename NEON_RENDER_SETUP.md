# DothPick: Neon PostgreSQL + Render setup

The live production database is PostgreSQL on Neon. Render runs the NiceGUI
application but does not store production picks on its local filesystem.

## 1. Create the Neon database

1. Create a Neon project.
2. In the Neon project dashboard, click **Connect**.
3. Copy the PostgreSQL connection string. A pooled connection string is a good
   fit for the web app.
4. Keep the connection string private.

## 2. Configure Render

In the existing Render web service, add these environment variables:

- `DATABASE_URL` = the Neon PostgreSQL connection string
- `STORAGE_SECRET` = a long random secret value
- `SEED_FROM_XLSX` = `true` for the first deployment

Do not put the real `DATABASE_URL` in GitHub.

The existing app already binds to `0.0.0.0` and reads Render's `PORT` value.

## 3. First deployment / data migration

The repository contains `database/database.xlsx` with the recovered users,
teams, games, picks, leaderboard data, settings, and history from the previous
local database.

At startup the app:

1. Connects to the database named by `DATABASE_URL`.
2. Creates any missing PostgreSQL tables.
3. Checks whether the `users` table is empty.
4. If it is empty and `SEED_FROM_XLSX=true`, imports `database/database.xlsx`.
5. Resets PostgreSQL ID sequences so new rows can be inserted normally.
6. Never imports the workbook over an already-populated database.

After the first successful deployment you can leave `SEED_FROM_XLSX=true`
because the import is guarded by the empty-database check, or set it to
`false` for extra protection.

## 4. Local testing

Without `DATABASE_URL`, the project deliberately falls back to a local SQLite
file at `database/dothpick.db` only when running locally. Render automatically
sets `RENDER=true`; if `DATABASE_URL` is missing there, startup fails instead of
silently storing production picks in an ephemeral SQLite file.

To test the same Neon database locally, create a `.env` file based on
`.env.example` and put your Neon connection string there, then run:

```powershell
python migrate_to_neon.py
python app.py
```

`migrate_to_neon.py` prints the backend and row counts so you can confirm that
the data reached Neon.

## 5. Excel is now an export, not the database

To create a readable Excel copy of the current live database:

```powershell
python export_database.py
```

This produces `database_export.xlsx`. It does not replace or modify the Neon
database.
