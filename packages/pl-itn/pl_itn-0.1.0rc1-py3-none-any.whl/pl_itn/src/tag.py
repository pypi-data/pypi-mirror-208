import pynini


def tag(tagger_fst, text):
    text = pynini.escape(text)

    lattice = text @ tagger_fst

    text = pynini.shortestpath(lattice, nshortest=1, unique=True).string()

    if text is None:
        raise ValueError("Tagger returned no output.")
    return text
