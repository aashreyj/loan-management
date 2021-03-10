def set_if_not_none(mapping, key, value):
        if value is not None:
            mapping[key] = value