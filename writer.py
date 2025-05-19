import re

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002500-\U00002BEF"  # chinese char
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642"
                           u"\u2600-\u2B55"
                           u"\u200d"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\ufe0f"  # dingbats
                           u"\u3030"
                           "]+", flags=re.UNICODE)


def _sanitize(row):
    return emoji_pattern.sub(r'', row).replace("\xb2", "")


def _compare(type, item_value, value):
    if type == 'equals':
        return value == item_value
    return False


def _filter(item, applied_filter):
    item_value = item[applied_filter['property']]
    operator = applied_filter['operator']
    type = applied_filter['type']
    values = applied_filter['value'] if isinstance(applied_filter['value'], list) else [applied_filter['value']]
    if operator == 'AND':
        result = True
        for value in values:
            result = result and _compare(type, item_value, value)
        return result
    if operator == 'OR':
        result = False
        for value in values:
            result = result or _compare(type, item_value, value)
        return result
    return False


def _filter_items(config, items):
    if 'filters' not in config:
        return items

    filtered_items = []
    for item in items:
        includes = any(map(lambda x: _filter(item, x), config['filters']))
        if includes:
            filtered_items.append(item)
    return filtered_items


def _write_item(file, item, properties, separator):
    try:
        file.write(_sanitize(separator.join(list(map(lambda x: str(item[x]), properties)))) + '\n')
    except Exception as e:
        print(f'Exception when writing {item}. {e}')


def _write(writer, file, items):
    properties = writer['properties']
    separator = writer['separator']
    file.write(separator.join(properties) + "\n")
    for item in items:
        _write_item(file, item, properties, separator)


def write(config, items):
    for writer in config:
        file_name = writer['file']
        print(f'Write {file_name}')
        with open(file_name, "w", encoding="utf-8") as f:
            filtered_items = _filter_items(writer, items)
            _write(writer, f, filtered_items)
