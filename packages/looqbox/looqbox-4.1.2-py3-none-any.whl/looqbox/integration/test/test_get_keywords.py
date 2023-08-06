import json
import os
import unittest

from looqbox.integration.integration_links import get_keyword
from looqbox.utils.utils import open_file


class TestGetKeywords(unittest.TestCase):
    # setup
    def setUp(self):
        file = open_file(os.path.dirname(__file__), "parser_reference", "venda_esse_ano_por_mes_por_estado.json")
        self.par = json.load(file)
        file.close()

        file = open_file(os.path.dirname(__file__), "parser_reference", "simple_test_par.json")
        self.test_par = json.load(file)
        file.close()

    def test_get_one_keyword(self):
        self.assertEqual([{'segment': 'venda', 'text': 'venda', 'id': 5}], get_keyword("venda", self.par))

    def test_get_two_keywords_two_calls_with_only_value(self):
        venda = get_keyword("venda", self.par, only_value=True)
        meta = get_keyword("meta", self.par, only_value=True)
        self.assertEqual([5, 6], [venda, meta])

    def test_get_two_keywords_one_call(self):
        self.assertEqual([{'segment': 'venda', 'text': 'venda', 'id': 5},
                          {'segment': 'meta', 'text': 'meta', 'id': 6}], get_keyword(["venda", "meta"], self.par))

    def test_get_two_keywords_one_call_with_only_value(self):
        self.assertEqual([5, 6], get_keyword(["venda", "meta"], self.par, only_value=True))

    def test_simplified_json_test(self):
        self.assertEqual(5, get_keyword("venda", self.test_par, only_value=True))
