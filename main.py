from configuration_reader import read_configuration
from items_loader import UrlHttpClient, ItemLoader
from processor import process_items
from store import create_store
from writer import write


def _load():
    store = create_store('json')
    cached_items = store.load(lambda: [], "resources/items")
    return cached_items
    #cached_items = {value['id']: value for index, value in enumerate(cached_items)}
    #return cached_items
    #config = read_configuration()['loader']
    #items = ItemLoader(config, UrlHttpClient()).load_items(cached_items)
    #store.store(items, 'items')
    #return items


def _process(items):
    config = read_configuration()['processor']
    return process_items(config, items)


def _write(items):
    config = read_configuration()['writers']
    write(config, items)


if __name__ == '__main__':
    items = _load()
    items = _process(items)
    _write(items)
