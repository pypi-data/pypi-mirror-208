import unittest
import json
import os

from unittest.mock import patch
from flowhigh.utils.converter import FlowHighSubmissionClass


class ConverterTest(unittest.TestCase):
    _response: {}

    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + "/input.json") as f:
            cls._response = json.loads(f.read())

    def test_convert(self):
        def __init__(self, sql):
            self._parsed_tree = self._convert_node(sql)

        with patch.object(FlowHighSubmissionClass, '__init__', __init__):
            parSeQL = FlowHighSubmissionClass(self._response)
            self.assertEqual(len(parSeQL.get_statements()), 1)

            statement = parSeQL.get_statements()[-1]
            self.assertIsNotNone(statement.ds[-1].in_)
            self.assertIsNotNone(statement.ds[-1].out)
