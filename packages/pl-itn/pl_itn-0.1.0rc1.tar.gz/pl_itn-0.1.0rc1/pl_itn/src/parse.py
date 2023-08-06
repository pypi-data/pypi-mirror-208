import re
from collections import OrderedDict
from typing import List

"""
Parses tokenized/classified text, e.g. 
'tokens { money { integer: "20" currency: "$" } } tokens { name: "left"}'

Args
    text: tokenized text
"""


def parse_tokens(text) -> List[dict]:
    parsed_tokens = []

    chunks = text.split("tokens")
    chunks_with_length = [c for c in chunks if len(c)]

    for token in chunks_with_length:
        current_level_dict = OrderedDict()
        current_level_dict["tokens"] = _parse_recursively(token)
        parsed_tokens.append(current_level_dict)

    return parsed_tokens


def _strip_braces_and_whitespaces(text):
    text = text.strip()
    text = text.lstrip("{")
    text = text.rstrip("}")
    text = text.strip()
    return text


def _parse_final_leaf(text):
    text = _strip_braces_and_whitespaces(text)
    keywords = re.findall(r"(\S+): ", text)
    values = re.findall(r"\"([^\"]+)\"", text)

    if len(keywords) != len(values):
        raise ValueError("Parsing tagged text into tokens failed.")

    yield from zip(keywords, values)


def _parse_recursively(text):
    text = _strip_braces_and_whitespaces(text)
    current_level_dict = OrderedDict()

    if "{" not in text:  # no nested dict
        for keyword, value in _parse_final_leaf(text):
            current_level_dict[keyword] = value

    else:
        keyword, text = text.split("{", 1)
        keyword = keyword.strip()
        current_level_dict[keyword] = _parse_recursively(text)

    return current_level_dict
