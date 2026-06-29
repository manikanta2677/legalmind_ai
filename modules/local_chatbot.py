import difflib

def answer_question(contract_text, question):

    lines = contract_text.split("\n")

    best_match = difflib.get_close_matches(
        question,
        lines,
        n=5,
        cutoff=0.1
    )

    if best_match:
        return "\n".join(best_match)

    return "No relevant information found."