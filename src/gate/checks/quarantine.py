from datetime import datetime, timezone


def check_quarantine(published: datetime | None, quarantine_days: int = 7) -> dict:
    if published is None:
        return {"ok": True, "days_old": None, "message": None}

    now = datetime.now(timezone.utc)
    days_old = (now - published).days

    if days_old < quarantine_days:
        return {
            "ok": False,
            "days_old": days_old,
            "message": f"Published {days_old} day(s) ago (quarantine window: {quarantine_days} days)",
        }

    return {"ok": True, "days_old": days_old, "message": None}
