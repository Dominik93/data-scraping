from commons.logger import get_logger
from dict_util import get_path_or_default

logger = get_logger("Processor")


class ProcessingException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


def _predicate(predicate: dict, value, default):
    for key in predicate:
        if value in predicate[key]:
            return key
    return default


def _template(template: str, value):
    return template.replace("{value}", value)


def _expression(expression: str, current_item, default):
    try:
        current = current_item['current']
        return eval(expression)
    except Exception as e:
        logger.warn("_expression", f"Eval {expression} failed fallback to default: {default}. Error: {e}")
        return default


def _process(item: dict, characteristic_provider):
    try:
        if 'template' in characteristic_provider:
            default = characteristic_provider['default']
            path = characteristic_provider['path']
            value = get_path_or_default(item, path, default)
            return _template(characteristic_provider['template'], value)
        if 'predicate' in characteristic_provider:
            default = characteristic_provider['default']
            path = characteristic_provider['path']
            value = get_path_or_default(item, path, default)
            return _predicate(characteristic_provider['predicate'], value, default)
        if 'expression' in characteristic_provider:
            default = characteristic_provider['default']
            return _expression(characteristic_provider['expression'], item, default)

        default = characteristic_provider['default']
        path = characteristic_provider['path']
        return get_path_or_default(item, path, default)
    except Exception as e:
        raise ProcessingException(f"Error when processing {item['id']} with {characteristic_provider}", e)


def process_items(processor_config: dict, items: list[dict]) -> list[dict]:
    processed_items = []
    for item in items:
        processed_item = {}
        item['current'] = processed_item
        for key in processor_config:
            characteristic_provider = processor_config[key]
            processed_item[key] = _process(item, characteristic_provider)
        processed_items.append(processed_item)
    return processed_items
