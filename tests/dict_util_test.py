import unittest

from dict_util import get_path_or_default


class DictUtilTestCase(unittest.TestCase):

    def test_return_default(self):
        actual = get_path_or_default({"item": {"not_id": "sample"}}, "$item.id", "")
        expected = ""
        self.assertEqual(expected, actual)

    def test_simple_path(self):
        actual = get_path_or_default({"item": {"id": "sample"}}, "$item.id", "")
        expected = "sample"
        self.assertEqual(expected, actual)

    def test_array_path(self):
        actual = get_path_or_default({"items": ["one", "two"]}, "$items.[-1]", "")
        expected = "two"
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
