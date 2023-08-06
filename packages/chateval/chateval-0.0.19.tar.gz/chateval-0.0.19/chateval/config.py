import os
from pathlib import Path

# Version
SCRIPTS_VERSION = "main"
HUB_DEFAULT_VERSION = "main"

# Hub
EP_ENDPOINT = os.environ.get("EP_ENDPOINT", "http://gair-nlp.co")
HUB_SCENARIO_URL = (
    "https://raw.githubusercontent.com/gair-nlp/data/{revision}"
    "/scenarios/{path}/{name}"
)


# Cache location
DEFAULT_XDG_CACHE_HOME = "~/.cache"
XDG_CACHE_HOME = os.getenv("XDG_CACHE_HOME", DEFAULT_XDG_CACHE_HOME)
# "~/.cache/gair-nlp"
DEFAULT_EP_CACHE_HOME = os.path.join(XDG_CACHE_HOME, "gair-nlp")
EP_CACHE_HOME = os.path.expanduser(os.getenv("EP_HOME", DEFAULT_EP_CACHE_HOME))


# "~/.cache/gair-nlp/scenario"
DEFAULT_EP_SCENARIO_CACHE = os.path.join(EP_CACHE_HOME, "scenario")
EP_SCENARIO_CACHE = Path(os.getenv("EP_SCENARIO_CACHE", DEFAULT_EP_SCENARIO_CACHE))


# "~/.cache/gair-nlp/modules"
DEFAULT_EP_MODULES_CACHE = os.path.join(EP_CACHE_HOME, "modules")
EP_MODULES_CACHE = Path(os.getenv("EP_MODULES_CACHE", DEFAULT_EP_MODULES_CACHE))

# "~/.cache/gair-nlp/scenario/downloads"
DOWNLOADED_DATASETS_DIR = "downloads"
DEFAULT_DOWNLOADED_SCENARIO_PATH = os.path.join(
    EP_SCENARIO_CACHE, DOWNLOADED_DATASETS_DIR
)
DOWNLOADED_SCENARIO_PATH = Path(
    os.getenv("EP_DATASETS_DOWNLOADED_SCENARIO_PATH", DEFAULT_DOWNLOADED_SCENARIO_PATH)
)


# "~/.cache/gair-nlp/scenario/downloads/extracted"
EXTRACTED_SCENARIO_DIR = "extracted"
DEFAULT_EXTRACTED_SCENARIO_PATH = os.path.join(
    DEFAULT_DOWNLOADED_SCENARIO_PATH, EXTRACTED_SCENARIO_DIR
)
EXTRACTED_SCENARIO_PATH = Path(
    os.getenv("EP_DATASETS_EXTRACTED_SCENARIO_PATH", DEFAULT_EXTRACTED_SCENARIO_PATH)
)


# File names
LICENSE_FILENAME = "LICENSE"
MODULE_NAME_FOR_DYNAMIC_MODULES = "scenario_modules"
SCENARIO_INFO_FILENAME = "scenario_info.json"


# General environment variables accepted values for booleans
ENV_VARS_TRUE_VALUES = {"1", "ON", "YES", "TRUE"}
ENV_VARS_TRUE_AND_AUTO_VALUES = ENV_VARS_TRUE_VALUES.union({"AUTO"})

# Offline mode
EP_SCENARIO_OFFLINE = (
    os.environ.get("EP_SCENARIO_OFFLINE", "AUTO").upper() in ENV_VARS_TRUE_VALUES
)
