import re


def get_path_or_default(item, path: str, default: any = '') -> dict | list | str | int:
    property_names = path.replace("$", "").split(".")
    return _get_or_default(item, property_names, default)


def _get_or_default(item, property_names: list, default: any = '') -> dict | list | str | int:
    result = item
    for property_name in property_names:
        if _is_array(property_name):
            result = _get_array_value(default, property_name, result)
        elif result is not None and property_name in result:
            result = result[property_name]
        else:
            return default
    return result


def _get_array_value(default, property_name, result):
    index = int(property_name.replace("[", "").replace("]", ""))
    try:
        result = result[index]
    except IndexError:
        result = default
    return result


def _is_array(property_name):
    return re.match('\[.*\]', property_name)
