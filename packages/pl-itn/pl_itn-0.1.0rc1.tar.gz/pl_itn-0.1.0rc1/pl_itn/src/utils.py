import re
from string import punctuation


def pre_process(text: str):
    text = text.lower()
    text = _surround_punctuation_with_spaces(text)
    text = _remove_multiple_whitespaces(text)
    return text


def post_process(text: str):
    text = _remove_multiple_whitespaces(text)
    return text


def _surround_punctuation_with_spaces(text: str):
    for punct in punctuation:
        text = text.replace(punct, f" {punct} ")
    return text


def _remove_multiple_whitespaces(text: str):
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text
