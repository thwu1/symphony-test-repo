import re
from datetime import datetime


def validate_email(email):
    """Return True if email looks valid, False otherwise."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def parse_due_date(date_str):
    """Parse an ISO-format date string and return a datetime, or None on failure."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def paginate_query(query, page, per_page=20):
    """Return a slice of *query* for the given 1-based *page*."""
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page
    items = query.limit(per_page).offset(offset).all()
    total = query.order_by(None).count()
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


def sanitize_string(value, max_length=None):
    """Strip whitespace and optionally truncate *value*."""
    if value is None:
        return None
    value = value.strip()
    if max_length and len(value) > max_length:
        value = value[:max_length]
    return value


def priority_label(priority):
    """Return a human-readable label for a numeric priority."""
    return {1: "low", 2: "medium", 3: "high"}.get(priority, "unknown")
