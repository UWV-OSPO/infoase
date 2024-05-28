def deep_update(orig_dict, new_dict):
    """
    Recursively updates the original dictionary with values from the new dictionary.
    If both original and new values are dictionaries, it recurses.
    Otherwise, it overwrites the original value with the new value.
    """
    for key, value in new_dict.items():
        if key in orig_dict:
            if isinstance(value, dict) and isinstance(orig_dict[key], dict):
                deep_update(orig_dict[key], value)
            else:
                orig_dict[key] = value
        else:
            orig_dict[key] = value
    return orig_dict
