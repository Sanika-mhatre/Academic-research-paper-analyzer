import re


def split_sentences(text):
    """
    Split text into sentences.

    - Splits using punctuation (., !, ?)
    - Also handles new lines
    """
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def add_issue(suggestions, mistake, message, correction):
    """
    Helper function to store grammar issues.

    Each issue contains:
    - mistake: incorrect text
    - message: type of error
    - correction: suggested fix
    """

    suggestions.append({
        "mistake": mistake[:100],      # limit size for UI
        "message": message,
        "correction": correction[:150]
    })


def grammar_check(text):
    """
    MAIN FUNCTION

    Performs grammar checking using rule-based NLP.
    Detects:
    - Repeated words
    - Spelling mistakes
    - Sentence structure issues
    - Punctuation errors
    """

    # If no text
    if not text or not text.strip():
        return {
            "accuracy": 0,
            "total_issues": 0,
            "suggestions": [],
            "message": "No text found."
        }

    suggestions = []

    # Clean spaces
    text = re.sub(r"\s+", " ", text.strip())

    # Split into sentences
    sentences = split_sentences(text)

    # -----------------------------------
    # 1. Repeated words ("the the")
    # -----------------------------------
    for match in re.finditer(r"\b(\w+)\s+\1\b", text, re.IGNORECASE):
        add_issue(
            suggestions,
            match.group(0),
            "Repeated word detected.",
            match.group(1)
        )

    # -----------------------------------
    # 2. Broken PDF words ("cita- tions")
    # -----------------------------------
    for match in re.finditer(r"\b[A-Za-z]+-\s+[A-Za-z]+\b", text):
        wrong = match.group(0)
        add_issue(
            suggestions,
            wrong,
            "Broken word detected due to PDF extraction.",
            wrong.replace("- ", "")
        )

    # -----------------------------------
    # 3. Missing space ("paper.This")
    # -----------------------------------
    for match in re.finditer(r"[.!?,;:][A-Za-z]", text):
        wrong = match.group(0)
        add_issue(
            suggestions,
            wrong,
            "Missing space after punctuation.",
            wrong[0] + " " + wrong[1]
        )

    # -----------------------------------
    # 4. Multiple punctuation ("!!")
    # -----------------------------------
    for match in re.finditer(r"([.!?]){2,}", text):
        add_issue(
            suggestions,
            match.group(0),
            "Unnecessary repeated punctuation.",
            match.group(0)[0]
        )

    # -----------------------------------
    # 5. Article mistakes (a/an)
    # -----------------------------------
    for match in re.finditer(r"\ba\s+([aeiouAEIOU]\w*)", text):
        word = match.group(1)
        add_issue(
            suggestions,
            match.group(0),
            "Article mistake detected.",
            f"an {word}"
        )

    for match in re.finditer(r"\ban\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]\w*)", text):
        word = match.group(1)
        add_issue(
            suggestions,
            match.group(0),
            "Article mistake detected.",
            f"a {word}"
        )

    # -----------------------------------
    # 6. Common grammar mistakes
    # -----------------------------------
    common_mistakes = {
        r"\bis are\b": "is",
        r"\bare is\b": "are",
        r"\bdoes not has\b": "does not have",
        r"\bdid not had\b": "did not have",
        r"\bmore better\b": "better",
        r"\bmost easiest\b": "easiest",
        r"\bcan able to\b": "can",
        r"\bi has\b": "I have",
        r"\bhe have\b": "he has",
        r"\bshe have\b": "she has",
        r"\bit have\b": "it has",
        r"\bthey has\b": "they have",
        r"\bwe has\b": "we have",
        r"\bthis are\b": "these are",
        r"\bthese is\b": "these are",
        r"\bthere is many\b": "there are many",
        r"\bone of the important\b": "one of the most important",
        r"\bdue to because\b": "because / due to"
    }

    for pattern, correction in common_mistakes.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            add_issue(
                suggestions,
                match.group(0),
                "Wrong sentence formation or grammar mistake detected.",
                correction
            )

    # -----------------------------------
    # 7. Spelling mistakes
    # -----------------------------------
    spelling_mistakes = {
        r"\bplagarism\b": "plagiarism",
        r"\bgrammer\b": "grammar",
        r"\bsentense\b": "sentence",
        r"\bselling mistake\b": "spelling mistake",
        r"\bseperate\b": "separate",
        r"\brecieve\b": "receive",
        r"\bdefinately\b": "definitely",
        r"\boccured\b": "occurred",
        r"\buntill\b": "until",
        r"\bwich\b": "which",
        r"\bteh\b": "the",
        r"\bthier\b": "their",
        r"\bbeleive\b": "believe",
        r"\bacheive\b": "achieve"
    }

    for pattern, correction in spelling_mistakes.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            add_issue(
                suggestions,
                match.group(0),
                "Spelling mistake detected.",
                correction
            )

    # -----------------------------------
    # 8. Sentence-level checks
    # -----------------------------------
    for sentence in sentences:
        words = re.findall(r"\b\w+\b", sentence)

        if not words:
            continue

        # Capital letter check
        first_letter = re.search(r"[A-Za-z]", sentence)
        if first_letter and sentence[first_letter.start()].islower():
            corrected = (
                sentence[:first_letter.start()]
                + sentence[first_letter.start()].upper()
                + sentence[first_letter.start() + 1:]
            )
            add_issue(
                suggestions,
                sentence,
                "Sentence should start with a capital letter.",
                corrected
            )

        # Missing punctuation
        if sentence[-1] not in ".!?":
            add_issue(
                suggestions,
                sentence,
                "Sentence may be missing ending punctuation.",
                sentence + "."
            )

        # Long sentence
        if len(words) > 35:
            add_issue(
                suggestions,
                sentence,
                "Sentence is too long and may reduce clarity.",
                "Break this sentence into shorter sentences."
            )

        # Too short sentence
        if len(words) < 3 and sentence.endswith("."):
            add_issue(
                suggestions,
                sentence,
                "Sentence seems incomplete.",
                "Rewrite as a complete sentence."
            )

    # -----------------------------------
    # Remove duplicate issues
    # -----------------------------------
    unique = []
    seen = set()

    for item in suggestions:
        key = (item["mistake"], item["message"], item["correction"])
        if key not in seen:
            unique.append(item)
            seen.add(key)

    # -----------------------------------
    # Calculate accuracy
    # -----------------------------------
    total_words = max(1, len(re.findall(r"\b\w+\b", text)))
    total_issues = len(unique)

    accuracy = max(0, 100 - ((total_issues / total_words) * 100))

    return {
        "accuracy": round(accuracy, 2),
        "total_issues": total_issues,
        "suggestions": unique[:30],
        "message": "Grammar check completed using custom rule-based checker."
    }