"""Export the live database to database_export.xlsx on demand."""

from pathlib import Path

from database.db import engine
from database.xlsx_store import export_database_to_xlsx


if __name__ == "__main__":
    output = export_database_to_xlsx(
        engine,
        Path("database_export.xlsx"),
    )
    print(f"Exported database to: {output.resolve()}")
