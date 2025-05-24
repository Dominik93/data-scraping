import unittest

from processor import process_items


class ProcessorTestCase(unittest.TestCase):
    def test_process_items_with_expression(self):
        processor_config = {"value": {"path": "$item.value", "default": 0},
                            "calculated_value": {"expression": "round(current['value'], 0)", "default": 0}}
        samples = [{"item": {"value": 2.3}}]
        actual = process_items(processor_config, samples)
        expected = [{"value": 2.3, "calculated_value": 2}]

        self.assertEqual(expected, actual)

    def test_process_items_with_template(self):
        processor_config = {"link": {"path": "$item.sample", "template": "http://{value}", "default": "-"}}
        samples = [{"item": {"sample": "value"}}]
        actual = process_items(processor_config, samples)
        expected = [{"link": "http://value"}]

        self.assertEqual(expected, actual)

    def test_process_items_with_predicate_default_value(self):
        processor_config = {
            "selected": {"path": "$item.sample", "predicate": {
                "Y": ["selected_one", "selected_two"],
                "N": ["not_selected"]
            }, "default": "-"}}
        samples = [{"item": {}}]
        actual = process_items(processor_config, samples)
        expected = [{"selected": "-"}]

        self.assertEqual(expected, actual)

    def test_process_items_with_predicate(self):
        processor_config = {"selected": {"path": "$item.sample", "predicate": {
            "Y": ["selected_one", "selected_two"],
            "N": ["not_selected"]
        }, "default": ""}}
        samples = [{"item": {"sample": "selected_one"}}, {"item": {"sample": "not_selected"}}]
        actual = process_items(processor_config, samples)
        expected = [{"selected": "Y"}, {"selected": "N"}]

        self.assertEqual(expected, actual)

    def test_process_items_with_array(self):
        processor_config = {"last": {"path": "$item.items.[-1]", "default": "-"}}
        samples = [{"item": {"items": ["value"]}}]
        actual = process_items(processor_config, samples)
        expected = [{"last": "value"}]

        self.assertEqual(expected, actual)

    def test_process_items_with_default_value(self):
        processor_config = {"title": {"path": "$item.sample", "default": "-"}}
        samples = [{"item": {}}]
        actual = process_items(processor_config, samples)
        expected = [{"title": "-"}]

        self.assertEqual(expected, actual)

    def test_process_items_with_simple_path(self):
        processor_config = {"title": {"path": "$item.sample", "default": "-"}}
        samples = [{"item": {"sample": "sample title"}}]
        actual = process_items(processor_config, samples)
        expected = [{"title": "sample title"}]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
