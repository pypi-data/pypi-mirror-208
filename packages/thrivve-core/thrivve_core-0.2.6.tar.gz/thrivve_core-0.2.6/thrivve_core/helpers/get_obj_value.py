def get_obj_value(_obj, key):
    if hasattr(_obj, '__dict__'):  # object
        return _obj.__dict__.get(key)

    elif isinstance(_obj, dict):  # dict
        return _obj.get(key)

    elif hasattr(_obj, key):  # class
        return getattr(_obj, key)


def set_obj_value(_obj, attr_name, attr_value):
    try:
        setattr(_obj, attr_name, attr_value)
    except AttributeError:
        _obj[attr_name] = attr_value
