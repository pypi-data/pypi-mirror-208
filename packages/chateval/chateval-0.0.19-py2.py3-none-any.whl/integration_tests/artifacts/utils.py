from __future__ import annotations

import os
import pathlib
from typing import Final

# OPTIONAL_TEST_SUITES = ['cli_all']
OPTIONAL_TEST_SUITES: list[str] = []


ARTIFACT_PATH: Final = os.path.join(os.path.dirname(pathlib.Path(__file__)), "./")

top_path: Final = os.path.join(
    pathlib.Path(__file__).parent.parent.absolute(),
)
