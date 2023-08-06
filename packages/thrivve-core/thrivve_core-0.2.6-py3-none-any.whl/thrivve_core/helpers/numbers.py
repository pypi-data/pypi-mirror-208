def fix_number(number):
    try:
        return round(float(number), 2)
    except Exception:
        pass

    return 0
