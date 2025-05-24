from commons.csv_writer import write as csv_write


def _compare(compare_type, item_value, value):
    if compare_type == 'equals':
        return value == item_value
    return False


def _filter(item, applied_filter):
    item_value = item[applied_filter['property']]
    operator = applied_filter['operator']
    compare_type = applied_filter['type']
    values = applied_filter['value'] if isinstance(applied_filter['value'], list) else [applied_filter['value']]
    if operator == 'AND':
        result = True
        for value in values:
            result = result and _compare(compare_type, item_value, value)
        return result
    if operator == 'OR':
        result = False
        for value in values:
            result = result or _compare(compare_type, item_value, value)
        return result
    return False


def _filter_items(config, items):
    if 'filters' not in config:
        return items

    filtered_items = []
    for item in items:
        includes = all(map(lambda x: _filter(item, x), config['filters']))
        if includes:
            filtered_items.append(item)
    return filtered_items


def write(config, items):
    for writer in config:
        file_name = writer['file']
        print(f'Write {file_name}')
        properties = writer['properties']
        separator = writer['separator']
        filtered_items = _filter_items(writer, items)
        csv_write(file_name, filtered_items, separator=separator, headers=properties)
