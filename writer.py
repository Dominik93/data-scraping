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


def _filter(item, applied_filter):
    value = item[applied_filter['property']]
    if applied_filter['type'] == 'equals':
        return value == applied_filter['value']
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


def write(config, items):
    for writer in config:
        file_name = writer['file']
        separator = writer['separator']
        print(f'Write {file_name}')
        with open(file_name, "w") as f:
            properties = writer['properties']
            f.write(separator.join(properties) + "\n")
            for item in _filter_items(writer, items):
                try:
                    row = separator.join(list(map(lambda x: str(item[x]), properties)))
                    f.write(emoji_pattern.sub(r'', row).replace("\xb2", "") + '\n')
                except Exception as e:
                    print(f'Exception when writing {item}. {e}')
