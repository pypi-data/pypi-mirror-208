import json
import os
import unittest

from looqbox.integration.integration_links import get_sso_attributes
from looqbox.utils.utils import open_file


class TestGetSsoAttributes(unittest.TestCase):

    def test_sso_attributes(self):
        """
        Test get_sso_attributes function
        """
        file = open_file(os.path.dirname(__file__), "parser_reference", "sso_attributes.json")
        par = json.load(file)
        file.close()

        file = open_file(os.path.dirname(__file__), "parser_reference", "sso_attributes2.json")
        par2 = json.load(file)
        file.close()

        self.assertEqual({"Seguranca": ["Group_1", "group_two", "G3"]}, get_sso_attributes(par))
        self.assertEqual({"Seguranca": ["Group_1", "group_two", "G3"]}, get_sso_attributes(par2))