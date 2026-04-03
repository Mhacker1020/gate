from datetime import datetime, timezone, timedelta

from gate.checks.quarantine import check_quarantine


def _days_ago(n: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=n)


def test_passes_when_old_enough():
    result = check_quarantine(_days_ago(10), quarantine_days=7)
    assert result["ok"] is True
    assert result["message"] is None


def test_fails_when_too_new():
    result = check_quarantine(_days_ago(3), quarantine_days=7)
    assert result["ok"] is False
    assert "3 day(s) ago" in result["message"]
    assert "7 days" in result["message"]


def test_passes_exactly_on_boundary():
    result = check_quarantine(_days_ago(7), quarantine_days=7)
    assert result["ok"] is True


def test_published_none_always_passes():
    result = check_quarantine(None)
    assert result["ok"] is True
    assert result["days_old"] is None


def test_custom_quarantine_window():
    result = check_quarantine(_days_ago(5), quarantine_days=14)
    assert result["ok"] is False

    result = check_quarantine(_days_ago(5), quarantine_days=3)
    assert result["ok"] is True


def test_days_old_is_reported():
    result = check_quarantine(_days_ago(3), quarantine_days=7)
    assert result["days_old"] == 3
