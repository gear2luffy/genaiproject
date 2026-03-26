"""
Utility functions for the AI Trading Platform.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json


def calculate_hash(data: str) -> str:
    """Calculate SHA256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def format_currency(amount: float) -> str:
    """Format number as currency string."""
    return f"${amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format number as percentage string."""
    return f"{value * 100:.{decimal_places}f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value


def get_trading_days(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Get list of trading days between two dates (excludes weekends)."""
    days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            days.append(current)
        current += timedelta(days=1)
    return days


def is_market_open() -> bool:
    """Check if US stock market is currently open."""
    now = datetime.utcnow()
    # Convert to EST (UTC-5)
    est_hour = now.hour - 5
    
    # Market hours: 9:30 AM - 4:00 PM EST
    if now.weekday() >= 5:  # Weekend
        return False
    
    if est_hour < 0:
        est_hour += 24
    
    market_open = 9.5  # 9:30 AM
    market_close = 16  # 4:00 PM
    
    return market_open <= est_hour < market_close


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string to max length with ellipsis."""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(value, max_value))


def normalize_score(score: float, min_val: float = -1, max_val: float = 1) -> float:
    """Normalize score to 0-1 range."""
    return (score - min_val) / (max_val - min_val)


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_to_json(data: Any) -> str:
    """Serialize data to JSON string, handling datetime objects."""
    return json.dumps(data, cls=DateTimeEncoder)


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string."""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    else:
        days = int(seconds / 86400)
        return f"{days}d ago"
