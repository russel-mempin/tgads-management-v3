def to_float(v: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0
    
def to_int(v: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0