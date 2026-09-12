def coerce_float(x) -> float:
    if x is None:
        return 0.0
    try:
        return float(str(x).strip())
    except (ValueError, TypeError):
        return 0.0

    raise ValueError(f"Cannot coerce {x} to float")
# coerce_float

def coerce_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    elif isinstance(val, str):
        val = val.strip().lower()
        if val in ['true','t','yes','y','1']:
            return True
        elif val in ['false','f','no','n','0']:
            return False
        else:
            return True
            # raise ValueError(f"Cannot coerce {val} to boolean")
    elif isinstance(val, int):
        return val != 0
        # if val == 1:
        #     return True
        # elif val == 0:
        #     return False
        # else:
        #     raise ValueError(f"Cannot coerce {val} to boolean")
    elif val is None:
        return False
    else:
        return True
        # raise ValueError(f"Cannot coerce {val} to boolean")

def coerce_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
