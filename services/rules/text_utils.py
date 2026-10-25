import unicodedata
from decimal import Decimal

def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)

    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    
    return " ".join(without_accents.casefold().split())


def format_decimal(value: Decimal) -> str:
    """Decimal('3.00') -> '3', Decimal('0.50') -> '0.5'."""
    return format(value.normalize(), "f")


def describe_minutes(minutes: int) -> str:
    """43200 -> '30 days', 120 -> '2 hours', 10 -> '10 minutes'."""
    if minutes % 1440 == 0:
        amount, unit = minutes // 1440, "day"
    elif minutes % 60 == 0:
        amount, unit = minutes // 60, "hour"
    else:
        amount, unit = minutes, "minute"
        
    return f"{amount} {unit}{'' if amount == 1 else 's'}"