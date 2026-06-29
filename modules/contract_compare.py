from difflib import SequenceMatcher


def compare_contracts(text1, text2):

    similarity = round(
        SequenceMatcher(
            None,
            text1.lower(),
            text2.lower()
        ).ratio() * 100,
        2
    )

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    added = list(words2 - words1)[:50]
    removed = list(words1 - words2)[:50]

    return {
        "similarity": similarity,
        "added": added,
        "removed": removed
    }