from services.logo_service import (
    update_all_missing_logos
)


updated_count = update_all_missing_logos()

print(
    f"Updated {updated_count} team logos."
)