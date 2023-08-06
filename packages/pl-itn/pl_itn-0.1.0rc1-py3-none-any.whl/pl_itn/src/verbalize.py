import logging
import pynini
import re

logger = logging.getLogger(__name__)


def verbalize(verbalize_fst, tags_permutations):
    for tagged_text_permutation in tags_permutations:
        
        tagged_text_permutation = re.sub(r" +", " ", tagged_text_permutation)
        tagged_text_permutation = tagged_text_permutation.strip()
        
        tagged_text_permutation = pynini.escape(tagged_text_permutation)
        logger.debug(tagged_text_permutation)
        lattice = tagged_text_permutation @ verbalize_fst

        if lattice.num_states():
            # permutation is syntactically correct (foreseen by verbalizer)
            return pynini.shortestpath(lattice, nshortest=1, unique=True).string()

    # no syntactically correct permutation found
    raise ValueError("Verbalizer returned no output")
