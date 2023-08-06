import pathlib
import unittest

from chateval import load

current_path = pathlib.Path(__file__).resolve().parent


class MyTestCase(unittest.TestCase):
    def test_scenario(self):

        scenario = load(f"{current_path}")
        predictions = [
            "My name is [name], and I am currently a student in your [class name]",
        ]

        result = scenario.evaluate(predictions)

        self.assertAlmostEqual(result["rouge1"]["value"], 0.21374, 3)
        self.assertAlmostEqual(result["count"]["value"], 14.0, 3)
