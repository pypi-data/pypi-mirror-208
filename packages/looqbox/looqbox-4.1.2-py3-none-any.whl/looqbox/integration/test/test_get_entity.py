import json
import os
import unittest

from looqbox.integration.integration_links import get_entity
from looqbox.utils.utils import open_file, load_json_from_relative_path


class TestGetEntity(unittest.TestCase):

    def test_get_entity_new_json_one_entity(self):
        """
        Test get_entity function with one entity in language version 2
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "meta_python.json")
        par = json.load(file)
        file.close()

        date = get_entity("$date", par)
        self.assertEqual([
            {"segment": "hoje", "text": "hoje", "value": [['2020-01-22', '2020-01-22']]}
        ], date)

        store = get_entity("$store", par)
        self.assertIsNone(store)

        default_value = get_entity("$undefined", par)  # TODO define default value behavior
        self.assertIsNone(default_value)

    def test_get_entity_new_json(self):
        """
        Test get_entity function with multiple entities in language version 2
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "venda_loja_sao_paulo_por_dia_essa_semana.json")
        par = json.load(file)
        file.close()

        date = get_entity("$date", par)
        self.assertEqual([
            {"segment": "essa semana", "text": "essa semana", "value": [['2021-01-11', '2021-01-17']]}
        ], date)

        mix_entities = get_entity(["$date", "$store"], par)
        self.assertEqual([
            {"segment": "essa semana", "text": "essa semana", "value": [['2021-01-11', '2021-01-17']]},
            {"segment": "da loja sao paulo", "value": [1]}
        ], mix_entities)

    def test_get_entity_old_json(self):
        """
        Test get_entity function in language version 1
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "test.json")
        par = json.load(file)
        file.close()

        date_value = get_entity("$date", par)
        self.assertEqual([['2019-01-08', '2019-01-08']], date_value)

        store_value = get_entity("$store", par)
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], store_value)

        default_value = get_entity("$undefined", par, only_value=True)
        self.assertIsNone(default_value)

        # mix_value = get_entity(["$date", "$datetime"], par)
        # self.assertEqual([['2019-01-08', '2019-01-08'], ['2019-01-08 00:00:00', '2019-01-08 00:00:00']], mix_value)

    def test_get_entity_new_json_default_value(self):
        """
        Test get_entity function with one entity in language version 2 and only_value set to True
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "meta_python.json")
        par = json.load(file)
        file.close()

        date = get_entity("$date", par, only_value=True)
        self.assertEqual([['2020-01-22', '2020-01-22']], date)

        store = get_entity("$store", par, only_value=True)
        self.assertIsNone(store)

        default_value = get_entity("$undefined", par, only_value=True)
        self.assertIsNone(default_value)

    def test_remove_unnecessary_nesting(self):
        par_path = os.path.join(os.path.dirname(__file__), "parser_reference", "monitoramento_de_erros.json")
        par = load_json_from_relative_path(par_path)
        company = get_entity("$company", par, only_value=True, entity_default=140)
        date = get_entity("$date", par, only_value=True)
        self.assertEqual(date, [['2023-04-01', '2023-04-30'], ['2023-05-01', '2023-05-31']])
        self.assertEqual([222], company)

    def test_get_entity_with_multiple_values(self):
        par_path = os.path.join(os.path.dirname(__file__), "parser_reference", "multiple_values.json")
        par = load_json_from_relative_path(par_path)
        centro = get_entity("$centro", par, only_value=True)
        self.assertEqual(centro, ["301198", "302112", "302121", "304323"])
