import pathlib
import unittest

from chateval import load

current_path = pathlib.Path(__file__).resolve().parent


class MyTestCase(unittest.TestCase):
    @unittest.skip("this requires openai's api key")
    def test_scenario(self):

        scenario = load(f"{current_path}")
        metric_model = scenario.get_default_setting_config()["metric_model"]
        result = scenario.evaluate(metric_model, "metric")

        print(result)

        self.assertAlmostEqual(result["accuracy"]["value"], 0, 3)
