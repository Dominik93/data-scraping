from dict_util import _get_path_or_default


def _predicate(predicate: dict, value, default):
    for key in predicate:
        if value in predicate[key]:
            return key
    return default


def _template(template: str, value):
    return template.replace("{value}", value)


# todo
def _expression(expression: str, item):
    return eval(expression)


def _process(item, characteristic_provider):
    if 'template' in characteristic_provider:
        default = characteristic_provider['default']
        path = characteristic_provider['path']
        value = _get_path_or_default(item, path, default)
        return _template(characteristic_provider['template'], value)
    if 'predicate' in characteristic_provider:
        default = characteristic_provider['default']
        path = characteristic_provider['path']
        value = _get_path_or_default(item, path, default)
        return _predicate(characteristic_provider['predicate'], value, default)
    if 'expression' in characteristic_provider:
        return _expression(characteristic_provider['expression'], item)

    default = characteristic_provider['default']
    path = characteristic_provider['path']
    return _get_path_or_default(item, path, default)


def process_items(processor_config, items: list[dict]) -> list[dict]:
    processed_items = []
    for item in items:
        processed_item = {}
        item['current'] = processed_item
        for key in processor_config:
            characteristic_provider = processor_config[key]
            processed_item[key] = _process(item, characteristic_provider)
        processed_items.append(processed_item)
    return processed_items
