from datetime import date, datetime, timedelta
from typing import Optional


def format_date(date_obj: date) -> str:
    """Format a date object as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def is_future_date(date_str: str) -> bool:
    """Check if a date string represents a future date."""
    try:
        date_obj = parse_date(date_str)
        return date_obj > date.today()
    except ValueError:
        return False


def generate_timestamp() -> str:
    """Generate a timestamp in format YYYYMMDD_HHMMSS."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
