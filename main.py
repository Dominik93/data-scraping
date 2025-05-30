import argparse

from commons.configuration_reader import read_configuration
from commons.store import create_store, Storage
from items_loader import UrlHttpClient, ItemLoader
from processor import process_items
from writer import write


def _load():
    store = create_store(Storage.JSON)
    stored_items = store.load(lambda: [], "resources/data/items")
    stored_items_by_id = {value['id']: value for index, value in enumerate(stored_items)}
    config = read_configuration("config").get('loader')
    loaded_items = ItemLoader(config, UrlHttpClient()).load_items(stored_items_by_id)
    new_items = _add_new_items(loaded_items, stored_items_by_id)
    store.store(new_items, 'resources/data/items')
    return new_items


def _add_new_items(loaded_items, stored_items_by_id):
    for item in loaded_items:
        if item['id'] not in stored_items_by_id:
            stored_items_by_id[item['id']] = item
    new_items = []
    for key in stored_items_by_id:
        new_items.append(stored_items_by_id[key])
    return new_items


def _load_stored():
    store = create_store(Storage.JSON)
    return store.load(lambda: [], "resources/data/items")


def _process(items_to_process):
    config = read_configuration("config").get_value('processor')
    return process_items(config, items_to_process)


def _write(items_to_write):
    config = read_configuration("config").get_value('writers')
    write(config, items_to_write)


def command_line_parser():
    parser = argparse.ArgumentParser(description='Data scraping')
    parser.add_argument("--actions", help='Coma separated actions to perform', required=True)
    args = parser.parse_args()
    return args.actions.split(",")


if __name__ == '__main__':
    actions = command_line_parser()
    items = []
    if 'load' in actions:
        items = _load()
    if 'load_stored' in actions:
        items = _load_stored()
    if 'process' in actions:
        items = _process(items)
    if 'write' in actions:
        _write(items)
