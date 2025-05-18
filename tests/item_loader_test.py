import unittest

from items_loader import ItemLoader, HttpClient

config = {
    "api": {
        "headers": {
            "X-HEADER": "X-HEADER-VALUE",
        }
    },
    "items_api": {
        "url": "http://smaple/{namespace}",
        "placeholders": {
            "namespace": "sample-namespace"
        },
        "query_params": {
            "param": "1",
            "page": "{iterable}"
        },
        "delay": {
            "min": 1,
            "max": 2
        },
        "response": {
            "compress": "None",
            "total_pages": "$totalPages",
            "return": "$items",
            "id": "$id"
        },
        "save_as": "item"
    },
    "details_api": {
        "url": "http://sample/{namespace}/{id}",
        "placeholders": {
            "namespace": "sample-namespace",
            "id": "$id"
        },
        "delay": {
            "min": 1,
            "max": 2
        },
        "response": {
            "compress": "None"
        },
        "save_as": "details"
    }
}


class MockHttpClient(HttpClient):

    def __init__(self, mock):
        self.mock = mock

    def call(self, req):
        return self.mock[req.full_url]


class ItemLoaderTestCase(unittest.TestCase):
    def test_load_items(self):
        mocks = {
            "http://smaple/sample-namespace?param=1&page=0": str.encode('{"items": [ {"id": "1"}], "totalPages": 1}'),
            "http://smaple/sample-namespace?param=1&page=1": str.encode('{"items": [ {"id": "2"}], "totalPages": 1}'),

            'http://sample/sample-namespace/1': str.encode('{ "data" : {} }'),
            "http://sample/sample-namespace/2": str.encode('{"data" : {}}'),
        }

        actual = ItemLoader(config, MockHttpClient(mocks)).load_items({})
        expected = [{'details': {"data": {}}, 'item': {'id': '1'}},
                    {'details': {"data": {}}, 'item': {'id': '2'}}]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
