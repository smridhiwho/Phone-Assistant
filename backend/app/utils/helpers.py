"""Utility helper functions."""

import re
from typing import Optional


def format_price(price_inr: int) -> str:
    """Format price in Indian Rupees with commas."""
    return f"₹{price_inr:,}"


def parse_price(price_str: str) -> Optional[int]:
    """Parse price string to integer."""
    if not price_str:
        return None

    # Remove currency symbols and spaces
    cleaned = re.sub(r'[₹,\s]', '', price_str.lower())

    # Handle 'k' suffix (e.g., "30k" -> 30000)
    if cleaned.endswith('k'):
        try:
            return int(float(cleaned[:-1]) * 1000)
        except ValueError:
            return None

    # Handle 'lakh' (e.g., "1 lakh" -> 100000)
    if 'lakh' in cleaned:
        try:
            num = re.search(r'[\d.]+', cleaned)
            if num:
                return int(float(num.group()) * 100000)
        except ValueError:
            return None

    # Try direct parse
    try:
        return int(cleaned)
    except ValueError:
        return None


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def normalize_brand_name(brand: str) -> str:
    """Normalize brand name to standard format."""
    brand_map = {
        "oneplus": "OnePlus",
        "one plus": "OnePlus",
        "samsung": "Samsung",
        "google": "Google",
        "pixel": "Google",
        "xiaomi": "Xiaomi",
        "mi": "Xiaomi",
        "redmi": "Xiaomi",
        "realme": "Realme",
        "vivo": "Vivo",
        "oppo": "Oppo",
        "nothing": "Nothing",
        "iqoo": "iQOO",
        "poco": "Poco",
        "motorola": "Motorola",
        "moto": "Motorola"
    }
    return brand_map.get(brand.lower(), brand.title())


def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    return [int(n) for n in re.findall(r'\d+', text)]


def is_valid_phone_query(query: str) -> bool:
    """Check if query is related to phones."""
    phone_keywords = [
        'phone', 'mobile', 'smartphone', 'device',
        'camera', 'battery', 'display', 'screen',
        'processor', 'ram', 'storage', 'android', 'ios',
        'samsung', 'oneplus', 'google', 'pixel', 'xiaomi',
        'realme', 'vivo', 'oppo', 'nothing', 'iqoo', 'poco',
        'buy', 'compare', 'recommend', 'suggest', 'best',
        'budget', 'flagship', 'gaming', 'cheap', 'affordable'
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in phone_keywords)
