import unittest
import os, sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from .clock_multi import check_time_format


class MyTestCase(unittest.TestCase):
    def test_check_time_format(self):
        result = check_time_format(25, 11)
        expect = False
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
