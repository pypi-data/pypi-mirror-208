import unittest

from caddo_file_parser.caddo_file_parser import CaddoFileParser


class FileReadingTest(unittest.TestCase):
    def test_file_reading(self):
        caddo_file_parser = CaddoFileParser()
        caddo_file_parser.read_data("results")
