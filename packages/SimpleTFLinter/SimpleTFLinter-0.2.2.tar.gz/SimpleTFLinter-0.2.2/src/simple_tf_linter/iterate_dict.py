def _value_path_pairs_for_list(list_obj, path):
    for index, item in enumerate(list_obj):
        new_path = f'{path}/{index}' if path else str(index)
        yield from value_path_pairs(item, new_path)


def _value_path_pairs_for_dict(dict_obj, path):
    for key, value in dict_obj.items():
        new_path = f'{path}/{key}' if path else key
        yield from value_path_pairs(value, new_path)


def value_path_pairs(obj, path=None):
    path = path or ''

    if isinstance(obj, dict):
        yield from _value_path_pairs_for_dict(obj, path)

    elif isinstance(obj, list):
        yield from _value_path_pairs_for_list(obj, path)
    
    elif isinstance(obj, (int, float, str)):
        yield obj, path
