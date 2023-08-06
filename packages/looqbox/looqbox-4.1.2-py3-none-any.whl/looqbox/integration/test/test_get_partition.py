import json
import os
import unittest

from looqbox.integration.integration_links import get_partition
from looqbox.utils.utils import open_file


class TestGetPartition(unittest.TestCase):

    def test_get_partition_new_json_one_partition(self):
        """
        Test get_partition function with one partition in language version 2
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "venda_por_dia_esse_mes.json")
        par = json.load(file)
        file.close()

        date_json = get_partition("$date", par)
        self.assertEqual([
            {"segment": "por dia", "text": "por dia", "value": ["byDay"]}
        ], date_json)

        store_json = get_partition("$store", par)
        self.assertEqual(None, store_json)

        default_value = get_partition("$undefined", par)
        self.assertIsNone(default_value)

    def test_get_partition_new_json(self):
        """
        Test get_partition function with multiple partitions in language version 2
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "venda_por_loja_por_dia.json")
        par = json.load(file)
        file.close()

        date = get_partition("$date", par)
        self.assertEqual([
            {"segment": "por dia", "text": "por dia", "value": ["byDay"]}
        ], date)

        mix_entities = get_partition(["$date", "$store"], par)
        self.assertEqual([
            {"segment": "por dia", "text": "por dia", "value": ["byDay"]},
            {"segment": "por loja", "text": "por loja", "value": []}
        ], mix_entities)

    def test_list_none_diff(self):
        file = open_file(os.path.dirname(__file__), "parser_reference", "venda_esse_ano_por_mes_por_estado.json")
        par = json.load(file)
        file.close()

        state = get_partition("$estado", par, only_value=True)
        self.assertEqual([], state)

    def test_list_none_diff_simplified_json(self):
        file = open_file(os.path.dirname(__file__), "parser_reference", "simple_test_par.json")
        par = json.load(file)
        file.close()

        state = get_partition("$country", par, only_value=True)
        self.assertEqual([], state)
