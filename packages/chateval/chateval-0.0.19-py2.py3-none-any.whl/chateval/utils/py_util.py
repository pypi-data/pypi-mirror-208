from __future__ import annotations

from hashlib import sha256
import logging
import re

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NO_ANSWER = "NO_ANSWER"


def get_yesno_from_text(text: str) -> dict:
    pattern = r"## (.+?)\n.+?([yn])"
    matches = re.findall(pattern, text, re.DOTALL)
    return {k: v for k, v in dict(matches).items()}


# example_text = """
# This is an example text with some ## important information about something.
# Please answer with either y or n: y
#
# ## Another piece of information that you should know about.
# Is this relevant? n
# """
#
# yesno_dict = get_yesno_from_text(example_text)
# print(yesno_dict)
# {'important information about something.': 'y',
# 'Another piece of information that you should know about.': 'n'}


def get_scores_from_text(text: str) -> dict:
    pattern = r"## (.+?)\n.+?(\d)/5"
    matches = re.findall(pattern, text, re.DOTALL)
    return {k: int(v) for k, v in dict(matches).items()}


def get_letter_from_data(data: str) -> str:
    last_y = (data.rfind("Y"), "Y")
    last_n = (data.rfind("N"), "N")

    if last_y[0] == -1 and last_n[0] == -1:
        return "YN"
    else:
        return max(last_y, last_n)[1]


def get_answer_from_data(data: str, answer_choices: list[str]) -> str:

    tuple_list = [(data.rfind(choice), choice) for choice in answer_choices]
    if sum([x[0] for x in tuple_list]) == -len(answer_choices):
        return NO_ANSWER
    else:
        return max(tuple_list)[1]


def dict_to_str(d: dict) -> str:
    return "\n" + "\n".join([f"{k}:{v}" for k, v in d.items()])


def list_to_str(d: list) -> str:
    return "\n" + "\n".join([f"{i+1}. {v}" for i, v in enumerate(d)])


def load_yaml(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def generate_format_func(pattern: str):
    """
    Generate a format function for a string with patter {}
    Args:
        pattern: a string with curly brackets, e.g., "[Query]:{query}\n[Documents]:{
        documents}\n[URL]:{url}"
    Returns:
    a function that takes an dictionary and returns a formatted string
    """

    arguments = re.findall(r"\{([^}]+)\}", pattern)

    if len(arguments) == 0:
        logger.warning(
            f"No arguments found in pattern: {pattern}, your input sample should be a "
            f"string, which will be regarded as the input"
        )
        return lambda d: d

    def format_func(input: dict[str, str]) -> str:
        """
        Generate a formatted string from the given dictionary.
        Args:
            input: a dictionary, for example
            input = {
                "query": "query",
                "documents": "documents",
                "url": "url"
            }
        Returns:
        a formatted string. for example: "[Query]:query\n[Documents]:documents\n[
        URL]:url"
        """

        result = pattern
        for arg in arguments:
            if arg not in input:
                raise KeyError(f"{arg} is not in your input sample")
            result = result.replace("{" + arg + "}", input[arg])

        return result

    return format_func


def hash_url_to_filename(url, etag=None):
    """
    Convert `url` into a hashed filename in a repeatable way.
    If `etag` is specified, append its hash to the url's, delimited
    by a period.
    If the url ends with .h5 (Keras HDF5 weights) adds '.h5' to the name
    so that TF 2.0 can identify it as a HDF5 file
    (see https://github.com/tensorflow/tensorflow/blob/00fad90125b18b80f
    e054de1055770cfb8fe4ba3/tensorflow/python/keras/engine/network.py#L1380)
    """
    url_bytes = url.encode("utf-8")
    url_hash = sha256(url_bytes)
    filename = url_hash.hexdigest()

    if etag:
        etag_bytes = etag.encode("utf-8")
        etag_hash = sha256(etag_bytes)
        filename += "." + etag_hash.hexdigest()

    if url.endswith(".py"):
        filename += ".py"

    return filename


def _hash_python_lines(lines: list[str]) -> str:
    filtered_lines = []
    for line in lines:
        line = re.sub(r"#.*", "", line)  # remove comments
        if line:
            filtered_lines.append(line)
    full_str = "\n".join(filtered_lines)

    # Make a hash from all this code
    full_bytes = full_str.encode("utf-8")
    return sha256(full_bytes).hexdigest()
