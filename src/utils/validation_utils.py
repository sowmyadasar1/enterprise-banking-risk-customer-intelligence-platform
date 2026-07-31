import re
from typing import Any

def is_valid_email(email: str) -> bool:
    """Validates an email address format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_uuid(val: Any) -> bool:
    """Checks if a value is a valid UUID string."""
    try:
        from uuid import UUID
        UUID(str(val), version=4)
        return True
    except ValueError:
        return False

def check_required_keys(data: dict, keys: list) -> bool:
    """Checks if a dictionary contains all required keys."""
    return all(k in data for k in keys)
