from looqbox.render.looqbox.base_looqbox_render import BrowserRender
from looqbox.utils.utils import open_file
from looqbox.objects.api import *
import plotly.graph_objs as go
import pandas as pd
import unittest
import json
import os


class TestLooqboxRender(unittest.TestCase):

    def setUp(self):

        self.render = BrowserRender()
        self.render.remove_nones = False

        self.message = ObjMessage("test message")
        self.html = ObjHTML("<div>Test HTML</div>")
        self.list = ObjList(["Item1", "Item2"])
        self.simple = ObjSimple("test simple")
        self.table = ObjTable()

        self.data = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    def test_message_render(self):
        file = open_file(os.path.dirname(__file__), "model_objects", "message_model.json")
        model_json = json.load(file)
        file.close()

        test_json = self.render.message_render(self.message)
        self.assertEqual(model_json, test_json)

    def test_html_render(self):
        file = open_file(os.path.dirname(__file__), "model_objects", "html_model.json")
        model_json = json.load(file)
        file.close()

        test_json = self.render.html_render(self.html)
        self.assertEqual(model_json, test_json)

    # def test_list_render(self):
    #
    #     model_json = json.loads("""
    #     {
    #      "objectType": "list",
    #      "title": [],
    #      "list": [
    #       "Item1",
    #       "Item2"
    #       ],
    #       "type": "list",
    #       "placeholder": "Escolha uma das opções abaixo:"}""")
    #
    #     test_json = json.loads(self.render.obj_list_render(self.list))
    #
    #     self.assertEqual(model_json, test_json)
    #

    def test_simple_render(self):
        file = open_file(os.path.dirname(__file__), "model_objects", "simple_object_model.json")
        model_json = json.load(file)
        file.close()

        test_json = self.render.simple_render(self.simple)
        self.assertEqual(model_json, test_json)

    def test_table_render(self):
        file = open_file(os.path.dirname(__file__), "model_objects", "table_model.json")
        model_json = json.load(file)
        file.close()

        self.table.data = self.data

        self.render.remove_nones = False
        test_json = self.render.table_render(self.table)

        self.assertEqual(model_json, test_json)

    def test_plotly_render(self):
        file = open_file(os.path.dirname(__file__), "model_objects", "plot_model.json")
        model_json = json.load(file)
        file.close()

        trace = go.Scatter(x=list(self.data['A']), y=list(self.data['B']))
        layout = go.Layout(title='title', yaxis=dict(title='test'))
        self.plotly = ObjPlotly([trace], layout=layout)

        test_json = self.render.plotly_render(self.plotly)
        self.assertEqual(model_json, test_json)
