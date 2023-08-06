# Global
from datetime import date, datetime
from typing import Optional


def ymd(string: str) -> Optional[date]:
    """Convert variable from type string to date

    Args:
        string (str): value with type string

    Return
        date: value with type date

    Usage
    >>> ymd(string="20221212")
    """
    parsor = None
    try:
        parsor = datetime.strptime(string, "%Y%m%d").date()
    except ValueError:
        pass

    return parsor
