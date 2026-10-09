"""Versioned, integer-only interval scheduling driven by aware server time."""
from datetime import datetime, timedelta, timezone

ALGORITHM_VERSION = "recall-v1"


def schedule_review(previous_interval_days: int, rating: str, reviewed_at: datetime):
    if type(previous_interval_days) is not int or not 0 <= previous_interval_days <= 365:
        raise ValueError("Prior interval must be an integer from 0 through 365.")
    if reviewed_at.tzinfo is None or reviewed_at.utcoffset() is None:
        raise ValueError("Review time must be timezone aware.")
    reviewed_at = reviewed_at.astimezone(timezone.utc)
    if rating == "again":
        interval = 0
        due = reviewed_at + timedelta(minutes=10)
    else:
        factors = {"hard": (12, 1), "good": (25, 1), "easy": (35, 4)}
        if rating not in factors:
            raise ValueError("Unknown recall rating.")
        numerator, minimum = factors[rating]
        interval = min(365, max(minimum, (previous_interval_days * numerator + 9) // 10))
        due = reviewed_at + timedelta(days=interval)
    return {"next_interval_days": interval, "next_review_at": due, "algorithm_version": ALGORITHM_VERSION}
