from enum import Enum
from pathlib import Path

from pynini import Fst, FstIOError

GrammarType = Enum("GrammarType", ["TAGGER", "VERBALIZER"])


class Grammar:
    def __init__(
        self, fst_path: Path, grammar_type: GrammarType, description: str = ""
    ):
        # try:
        self._fst = Fst.read(str(fst_path))
        self._type = grammar_type
        # except FstIOError as e:
        self._fst_path = fst_path
        self._description = description

    @property
    def fst(self):
        return self._fst

    @property
    def grammar_type(self):
        return self._type

    @property
    def fst_path(self):
        return self._fst_path

    @property
    def description(self):
        return self._description
