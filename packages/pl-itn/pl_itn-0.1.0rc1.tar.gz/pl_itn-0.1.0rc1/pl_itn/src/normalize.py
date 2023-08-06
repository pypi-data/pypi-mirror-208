import logging
import pynini
from pathlib import Path

from pl_itn.src.grammar import Grammar, GrammarType
from pl_itn.src.tag import tag
from pl_itn.src.parse import parse_tokens
from pl_itn.src.permute import generate_permutations
from pl_itn.src.restore_uppercase import restore_uppercase
from pl_itn.src.restore_whitespace import restore_whitespaces
from pl_itn.src.tag import tag
from pl_itn.src.utils import pre_process, post_process
from pl_itn.src.verbalize import verbalize

logger = logging.getLogger(__name__)

package_root = Path(__file__).parents[1]


class NormalizationError(Exception):
    ...


class Normalizer:
    def __init__(
        self,
        tagger_fst_path: Path = package_root / "grammars/tagger.fst",
        verbalizer_fst_path: Path = package_root / "grammars/verbalizer.fst",
    ):
        self._tagger = Grammar(tagger_fst_path, GrammarType.TAGGER)
        self._verbalizer = Grammar(verbalizer_fst_path, GrammarType.VERBALIZER)

    @property
    def tagger(self):
        return self._tagger

    @property
    def verbalizer(self):
        return self._verbalizer

    def set_grammar(
        self, grammar_fst_path: Path, grammar_type: GrammarType, description: str = ""
    ):
        if grammar_type == GrammarType.TAGGER:
            self._tagger = Grammar(grammar_fst_path, GrammarType.TAGGER, description)
        else:
            self._verbalizer = Grammar(
                grammar_fst_path, GrammarType.VERBALIZER, description
            )

    def __call__(self, text: str) -> str:
        return self.normalize(text)

    def normalize(self, text: str) -> str:
        logger.debug(f"input: {text}")

        preprocessed_text = pre_process(text)

        if not preprocessed_text:
            logger.info("Empty input string")
            return text

        logger.debug(f"pre_process(): {preprocessed_text}")

        try:
            tagged_text = tag(self.tagger.fst, preprocessed_text)
            logger.debug(f"tag(): {tagged_text}")

            tokens = parse_tokens(tagged_text)
            logger.debug(f"parse(): {tokens}")

            tags_reordered = generate_permutations(tokens)
            logger.debug(f"generate_permutations(): {tags_reordered}")

            verbalized_text = verbalize(self.verbalizer.fst, tags_reordered)
            logger.debug(f"verbalize(): {verbalized_text}")

            postprocessed_text = post_process(verbalized_text)
            logger.debug(f"post_process(): {postprocessed_text}")

            uppercase_restored = restore_uppercase(text, postprocessed_text)
            logger.debug(f"restore_uppercase(): {uppercase_restored}")

            whitespaces_restored = restore_whitespaces(text, uppercase_restored, tokens)
            logger.debug(f"restore_whitespaces(): {whitespaces_restored}")

            return whitespaces_restored

        except Exception as e:
            logger.error(e)
            raise NormalizationError(e)
