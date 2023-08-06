from __future__ import annotations

import os
import unittest

from integration_tests.artifacts.utils import ARTIFACT_PATH

from chateval.chateval import ChatEval


class MyTestCase(unittest.TestCase):
    def test_load_metrics_from_config(self):
        artifact_path = os.path.join(ARTIFACT_PATH, "yaml_config")
        write_email_config_folder = os.path.join(artifact_path, "write_email")

        chateval = ChatEval(write_email_config_folder)

        self.assertEqual(len(chateval.metrics), 2)
