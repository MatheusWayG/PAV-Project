from datetime import datetime

def now() -> datetime:
    return datetime.now()

def to_naive_local(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    
    return value.astimezone().replace(tzinfo=None)