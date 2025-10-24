"""
Utility helper functions for AetherSegment AI
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List


def generate_segment_id(campaign_objective: str, timestamp: datetime = None) -> str:
    """
    Generate a unique segment ID based on campaign objective and timestamp
    
    Args:
        campaign_objective: The natural language campaign objective
        timestamp: Optional timestamp (defaults to now)
    
    Returns:
        A unique segment ID string
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Create a hash of the campaign objective
    objective_hash = hashlib.md5(campaign_objective.encode()).hexdigest()[:8]
    
    # Format: SEG_YYYYMMDD_HASH
    date_str = timestamp.strftime('%Y%m%d')
    return f"SEG_{date_str}_{objective_hash.upper()}"


def parse_time_constraint(constraint_str: str) -> timedelta:
    """
    Parse a time constraint string into a timedelta
    
    Args:
        constraint_str: String like "48_hours", "7_days", "2_weeks"
    
    Returns:
        A timedelta object
    """
    parts = constraint_str.lower().split('_')
    
    if len(parts) < 2:
        return timedelta(days=7)  # Default to 7 days
    
    value = int(parts[0])
    unit = parts[1]
    
    if 'hour' in unit:
        return timedelta(hours=value)
    elif 'day' in unit:
        return timedelta(days=value)
    elif 'week' in unit:
        return timedelta(weeks=value)
    elif 'month' in unit:
        return timedelta(days=value * 30)
    else:
        return timedelta(days=7)


def format_currency(value: float) -> str:
    """Format a numeric value as currency"""
    return f"${value:,.2f}"


def calculate_percentile(value: float, min_val: float = 0.0, max_val: float = 1.0) -> int:
    """
    Calculate percentile from a score (0-1 range)
    
    Args:
        value: The score value
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Percentile (0-100)
    """
    if max_val == min_val:
        return 50
    
    normalized = (value - min_val) / (max_val - min_val)
    return int(normalized * 100)


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize a string to be used as a SQL identifier
    
    Args:
        identifier: The string to sanitize
    
    Returns:
        Sanitized identifier safe for SQL
    """
    # Remove special characters, keep only alphanumeric and underscore
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in identifier)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    
    return sanitized.lower()


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON with a default fallback
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def extract_keywords(text: str, stop_words: List[str] = None) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Input text
        stop_words: List of words to exclude
    
    Returns:
        List of keywords
    """
    if stop_words is None:
        stop_words = ['a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 
                      'to', 'for', 'of', 'with', 'by', 'from']
    
    # Simple word extraction
    words = text.lower().split()
    keywords = [word.strip('.,!?;:') for word in words 
                if word.lower() not in stop_words and len(word) > 2]
    
    return list(set(keywords))

