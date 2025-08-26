from datetime import datetime, timezone

def now_utc():
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

def now_utc_iso():
    """ISO-8601 string with Z suffix."""
    return now_utc().isoformat().replace("+00:00", "Z")