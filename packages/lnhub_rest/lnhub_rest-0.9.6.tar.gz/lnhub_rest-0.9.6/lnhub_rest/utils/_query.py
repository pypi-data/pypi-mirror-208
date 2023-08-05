def filter_null_from_dict(d: dict):
    return {key: value for key, value in d.items() if value is not None}
