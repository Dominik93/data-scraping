from configuration_reader import read_configuration
from items_loader import UrlHttpClient, ItemLoader
from processor import process_items
from store import create_store
from writer import write


def _load():
    store = create_store('json')
    stored_items = store.load(lambda: [], "resources/items")
    stored_items_by_id = {value['id']: value for index, value in enumerate(stored_items)}
    config = read_configuration()['loader']
    loaded_items = ItemLoader(config, UrlHttpClient()).load_items(stored_items_by_id)
    new_items = _add_new_items(loaded_items, stored_items_by_id)
    store.store(new_items, 'resources/items')
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
    store = create_store('json')
    return store.load(lambda: [], "resources/items")


def _process(items_to_process):
    config = read_configuration()['processor']
    return process_items(config, items_to_process)


def _write(items_to_write):
    config = read_configuration()['writers']
    write(config, items_to_write)


if __name__ == '__main__':
    items = _load()
    items = _process(items)
    _write(items)
