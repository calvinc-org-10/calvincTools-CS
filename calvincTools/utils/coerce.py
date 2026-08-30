def coerce_float(x) -> float:
    if x is None:
        return 0.0
    try:
        return float(str(x).strip())
    except (ValueError, TypeError):
        return 0.0

    raise ValueError(f"Cannot coerce {x} to float")
# coerce_float
