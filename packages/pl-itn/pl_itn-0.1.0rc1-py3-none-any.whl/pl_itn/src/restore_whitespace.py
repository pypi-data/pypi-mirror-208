import re
import string
from typing import List, Dict


def restore_whitespaces(original: str, normalized: str, tokens: List[Dict]) -> str:
    """
    Finite State Transducers normalization loses record of the original whitespace.
    Each token of the normalized text is separated by a single space, no matter if there was no, single or multiple spaces in the given spot originally.
            `! (dwunasta)` -> `! ( 12 )`

    WhitespaceRestorer detects words which have not been transformed by the normalizer (mostly punctuation marks) and restores the original spaces around them.
            `! (dwunasta)` -> `! ( 12 )` -> `! (12)`

    Args:
        original (str): Input phrase, for example "Jest godzina piętnasta trzydzieści."
        normalized (str): ITN output phrase, for example "Jest godzina 15:30 ."
        tokens ([dict]): parsed tokens from FST tagging, for example
            `[OrderedDict([('tokens', OrderedDict([('name', 'jest')]))]), OrderedDict([('tokens', OrderedDict([('time', OrderedDict([('complement', 'godzina'), ('hours', '15'), ('minutes', '30')]))]))]), OrderedDict([('tokens', OrderedDict([('name', '.')]))])]`
    """
    lower_list = lambda x: [w.lower() for w in x]

    normalized = normalized.split(" ")
    normalized_lower = lower_list(normalized)

    original = re.split(
        rf"(\s+|[{string.punctuation}])", original
    )  # ie. ['Jest', ' ', 'godzina', ' ', 'piętnasta', ' ', 'trzydzieści', '.']
    original = [w for w in original if len(w) > 0]
    original_lower = lower_list(original)

    restored = ""

    for token in tokens:
        token = token[
            "tokens"
        ]  # OrderedDict([('tokens', OrderedDict([('name', 'jest')]))]) -> OrderedDict([('name', 'jest')])

        # Tokens tagged as `name` have not been transformed during FST normalization.
        # ie. `OrderedDict([('name', 'jest')])` or `OrderedDict([('name', '.')])`
        is_original_form = lambda x: x.get("name")

        if is_original_form(token):
            word = token["name"]

            # the word has not been transformed, so it can be found both in the normalized and original texts
            index_normalized = normalized_lower.index(word)
            index_original = original_lower.index(word)

            # if the word is preceded by transformed words in the normalized text, add them first
            restored += " ".join(normalized[:index_normalized])

            # compose a group of the word itself sorrounded by its original white spaces. Add it to the output.
            def maybe_get_whitespace(input_list, index):
                try:
                    value = input_list[index]
                except IndexError:
                    return ""
                if re.match("^\s+$", value):
                    return value
                return ""

            word_with_spaces = (
                maybe_get_whitespace(original, index_original - 1)
                + original[index_original]
                + maybe_get_whitespace(original, index_original + 1)
            )
            restored += word_with_spaces

            if maybe_get_whitespace(original, index_original + 1):
                # Include trailing whitespace to the processed part
                index_original += 1

            # Remove processed input
            def slice_head(input_list, index):
                return input_list[index + 1 :]

            normalized = slice_head(normalized, index_normalized)
            normalized_lower = slice_head(normalized_lower, index_normalized)
            original = slice_head(original, index_original)
            original_lower = slice_head(original_lower, index_original)

    restored += " ".join(normalized)
    return restored
