from datetime import datetime, date, timedelta
from typing import Union, List

def get_current_timestamp() -> str:
    """Returns current UTC timestamp as ISO format string."""
    return datetime.utcnow().isoformat()

def date_to_string(dt: Union[datetime, date], fmt: str = "%Y-%m-%d") -> str:
    """Converts a date or datetime object to a formatted string."""
    return dt.strftime(fmt)

def string_to_date(dt_str: str, fmt: str = "%Y-%m-%d") -> datetime:
    """Parses a string into a datetime object."""
    return datetime.strptime(dt_str, fmt)

def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """Generates a list of dates between start_date and end_date (inclusive)."""
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]
