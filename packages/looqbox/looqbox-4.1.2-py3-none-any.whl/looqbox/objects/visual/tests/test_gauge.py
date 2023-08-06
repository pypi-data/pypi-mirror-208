import unittest
from looqbox.objects.looq_object import LooqObject
from looqbox.objects.component_utility.css_option import CssOption as css
from looqbox.objects.visual.looq_gauge import ObjGauge
from collections.abc import Iterable


class TestGauge(unittest.TestCase):
    """
    Test Gauge Component
    """

    def setUp(self):
        sample_data = {
            "value": 0.2,
            "label": "A"
        }
        self.gauge_0 = ObjGauge(sample_data, css_options=[css.Width(200), css.Height(100)])
        self.gauge_1 = ObjGauge(sample_data, css_options=[css.Width(250), css.Height(25)], render_condition=False)
        self.gauge_2 = ObjGauge(sample_data, [sample_data], sample_data)

    def test_instance(self):
        self.assertIsInstance(self.gauge_0, LooqObject)

    def test_properties_access(self):
        self.assertIn(css.Width, self.gauge_0.css_options)

    def test_render_condition(self):
        self.assertFalse(self.gauge_1.render_condition)

    def test_gauge_input_type(self):
        self.assertIsInstance(self.gauge_0.traces, Iterable)

    def test_gauge_comparison(self):
        self.assertFalse(self.gauge_0 == self.gauge_1)
        self.assertTrue(self.gauge_0 == self.gauge_0)

    def test_gauge_hstack(self):
        self.assertEqual(len(self.gauge_2.traces), 3)

    def test_gauge_default_colors(self):
        colors = {
            "0": "#F46F5D",
            "0.4": "#F4E85D",
            "0.8": "#40DA62"
        }

        data_with_color = {
            "value": 0.2,
            "label": "A",
            "color": colors
        }
        gauge_with_colors = ObjGauge(data_with_color, css_options=[css.Width(200), css.Height(100)])
        gauge_with_colors._get_default_style()
        gauge_with_colors.add_default_color_schema()

        model_gauge = self.gauge_0
        model_gauge._get_default_style()
        model_gauge.add_default_color_schema()

        self.assertEqual(gauge_with_colors.traces, model_gauge.traces)

    def test_gauge_color_priority(self):

        data_without_color_default = {
            "value": 0.2,
            "label": "A",
            "color": "#40DA62"
        }

        model_gauge = ObjGauge(data_without_color_default, css_options=[css.Width(200), css.Height(100)])
        model_gauge._get_default_style()
        model_gauge.add_default_color_schema()

        self.assertTrue(model_gauge.traces[0].get("color") == "#40DA62")


if __name__ == '__main__':
    unittest.main()
