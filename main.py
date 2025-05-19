from configuration_reader import read_configuration
from items_loader import UrlHttpClient, ItemLoader
from processor import process_items
from store import create_store
from writer import write


def _load():
    store = create_store('json')
    cached_items = store.load(lambda: [], "resources/items")
    cached_items = {value['id']: value for index, value in enumerate(cached_items)}
    config = read_configuration()['loader']
    loaded_items = ItemLoader(config, UrlHttpClient()).load_items(cached_items)
    store.store(loaded_items, 'resources/items')
    return loaded_items


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
