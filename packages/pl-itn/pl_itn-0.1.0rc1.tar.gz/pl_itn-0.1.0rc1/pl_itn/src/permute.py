import itertools
from collections import OrderedDict
from typing import List


def generate_permutations(tokens: List[dict]):
    """
    Initiate generate_permutations_recursive() on tokens
    with no processed_left_string.
    """
    return _generate_permutations_recursive(tokens, processed_left_string="", index=0)


def _generate_permutations_recursive(tokens, processed_left_string, index):
    """
    One by one sequentially, each input substructure generates permutations.
    Each permutation starts a new output instance.
    """
    if index >= len(tokens):  # no more input to process, exit recurency
        yield processed_left_string

    else:
        cursor_permutations = _permute(tokens[index])

        for permutation in cursor_permutations:
            yield from _generate_permutations_recursive(
                tokens, processed_left_string + permutation, index + 1
            )


def _permute(token):
    results = []

    permutations = itertools.permutations(token.items())
    for permutation in permutations:
        # serialize nested list-dict structure to a flat list of strings
        converted_permutation = [""]  # output structure: list of strings

        for key, value in permutation:
            if isinstance(value, str):
                pattern = [f'{key}: "{value}" ']
                converted_permutation = [
                    "".join(x)
                    for x in itertools.product(converted_permutation, pattern)
                ]
            elif isinstance(value, bool):
                pattern = [f"{key}: {value} "]
                converted_permutation = [
                    "".join(x)
                    for x in itertools.product(converted_permutation, pattern)
                ]
            elif isinstance(value, OrderedDict):
                recursive_permutation = _permute(value)
                prefix = [f" {key} {{ "]
                suffix = [" } "]
                converted_permutation = [
                    "".join(x)
                    for x in itertools.product(
                        converted_permutation, prefix, recursive_permutation, suffix
                    )
                ]
            else:
                raise ValueError(
                    "Permuter error! Substructure type is incorrect, something went really wrong."
                )

        results.extend(converted_permutation)

    return results
