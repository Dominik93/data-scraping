import unittest

from processor import process_items

processor_config = {
    "title": {"path": "$item.title", "default": "-"},
    "description": {"path": "$item.description", "default": "-"},
    "last": {"path": "$item.items.[-1]", "default": "-"},
    "link": {"path": "$item.title", "template": "http://{value}", "default": "-"},
    "selected": {"path": "$item.title", "predicate": {
        "Y": ["selected_one", "selected_two"],
        "N": ["not_selected"]
    }, "default": ""},
    "value": {"path": "$item.value", "default": 0},
    #"calculated_value": {"expression": "round( current['value'], 2 )"}
}


class ProcessorTestCase(unittest.TestCase):
    def test_proces_items(self):
        samples = []
        samples.append({"item": {"title": "sample title", "value": 1, "items": ["one"]}})
        samples.append({"item": {"title": "selected_one", "value": 2.5,"items": []}})
        samples.append({"item": {"title": "selected_two", "value": 5,"items": ["one", "two"]}})
        samples.append({"item": {"title": "not_selected"}})
        actual = process_items(processor_config, samples)
        expected = []
        expected.append(
            {"title": "sample title", "description": "-", "last": "one", "link": "http://sample title", "selected": "", "value":1})
        expected.append(
            {"title": "selected_one", "description": "-", "last": "-", "link": "http://selected_one", "selected": "Y", "value":2.5})
        expected.append({"title": "selected_two", "description": "-", "last": "two", "link": "http://selected_two",
                         "selected": "Y", "value":5})
        expected.append(
            {"title": "not_selected", "description": "-", "last": "-", "link": "http://not_selected", "selected": "N", "value":0})
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
