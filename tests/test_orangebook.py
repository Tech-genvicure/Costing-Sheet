from app.services.orangebook_service import (
    build_orange_book_summary,
    build_commercial_summary
)

raw = build_orange_book_summary(
    "WEGOVY"
)

summary = build_commercial_summary(
    raw
)

print(summary)