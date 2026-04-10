"""
Helper utility functions.

Demonstrates:
- Pure utility functions
- Type hints
- Reusable logic
"""

import re
from typing import Any, List, TypeVar

T = TypeVar("T")


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text.
    
    Args:
        text: The text to convert to a slug
        
    Returns:
        str: URL-friendly slug
        
    Example:
        >>> generate_slug("Hello World!")
        "hello-world"
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Remove special characters
    slug = re.sub(r"[^\w\s-]", "", slug)
    
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    
    # Remove leading/trailing hyphens
    return slug.strip("-")


def mask_email(email: str) -> str:
    """
    Mask an email address for privacy.
    
    Args:
        email: The email address to mask
        
    Returns:
        str: Masked email address
        
    Example:
        >>> mask_email("john.doe@example.com")
        "j***e@example.com"
    """
    if "@" not in email:
        return email
    
    local, domain = email.rsplit("@", 1)
    
    if len(local) <= 2:
        masked_local = local[0] + "*" * len(local[1:])
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def paginate_list(
    items: List[T],
    page: int = 1,
    page_size: int = 20
) -> tuple[List[T], int]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (paginated items, total count)
        
    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> paginate_list(items, page=1, page_size=2)
        ([1, 2], 5)
    """
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    
    return items[start:end], total


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncated
        
    Returns:
        str: Truncated string
        
    Example:
        >>> truncate_string("Hello World", 8)
        "Hello..."
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.
    
    Args:
        snake_str: String in snake_case
        
    Returns:
        str: String in camelCase
        
    Example:
        >>> snake_to_camel("hello_world")
        "helloWorld"
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convert camelCase to snake_case.
    
    Args:
        camel_str: String in camelCase
        
    Returns:
        str: String in snake_case
        
    Example:
        >>> camel_to_snake("helloWorld")
        "hello_world"
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def format_bytes(size: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        str: Human-readable size string
        
    Example:
        >>> format_bytes(1024)
        "1.00 KB"
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
        
    Example:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [
        items[i:i + chunk_size]
        for i in range(0, len(items), chunk_size)
    ]


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary to merge (takes precedence)
        
    Returns:
        dict: Merged dictionary
        
    Example:
        >>> deep_merge({"a": 1, "b": {"c": 2}}, {"b": {"d": 3}})
        {"a": 1, "b": {"c": 2, "d": 3}}
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
