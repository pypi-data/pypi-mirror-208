def restore_uppercase(original: str, normalized: str):
    original = original.split()
    normalized = normalized.split()
    restored = normalized[:]

    original_index, original_limit = 0, len(original)
    normalized_index, normalized_limit = 0, len(normalized)

    def finished():
        return normalized_index >= normalized_limit or original_index >= original_limit

    def match():
        if finished():  # out of index guardian
            return False
        return normalized[normalized_index] == original[original_index].lower()

    def next_original_index():
        nonlocal original_index
        original_index += 1
        return not finished()  # False if index out of range

    def next_normalized_index():
        nonlocal normalized_index
        normalized_index += 1

    def restore():
        restored[normalized_index] = original[original_index]
        next_original_index()
        next_normalized_index()

    while not finished():
        if match():
            restore()
            break

        # check the next pair
        next_original_index()
        next_normalized_index()
        if match():
            restore()
            break

        # look for shifted match
        checkpoint = original_index
        while next_original_index():
            if match():
                restore()
                break

        # no match, the word has been inverse normalized
        original_index = checkpoint
        next_normalized_index()
        next_original_index()

    return " ".join(restored)
