def fix_number(number):
    try:
        return round(float(number), 2)
    except ValueError:
        pass

    return 0
