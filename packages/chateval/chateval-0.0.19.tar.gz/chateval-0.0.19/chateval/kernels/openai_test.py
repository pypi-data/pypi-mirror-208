import unittest

from chateval.kernels.openai import OpenAIChat, OpenAICompletion


class MyTestCase(unittest.TestCase):
    def test_completion(self):

        code = "Translate this sentence into Chinese: Hello, my name is Jack."
        result = OpenAICompletion().execute(code)
        print(result)

        result = OpenAIChat().execute(
            [
                {"role": "system", "content": "I will help with anything you need."},
                {"role": "user", "content": code},
            ]
        )
        print(result)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
