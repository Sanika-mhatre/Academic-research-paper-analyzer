import re


def clean_extracted_text(text):
    """
    Clean text extracted from PDF.

    Purpose:
    - Fix broken words caused by PDF extraction
    - Remove extra spaces and newlines
    """

    # If text is empty or None → return empty string
    if not text:
        return ""

    # Fix broken words:
    # Example: "cita- tions" → "citations"
    text = re.sub(r"-\s+", "", text)

    # Replace multiple spaces/newlines with single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing spaces
    return text.strip()


def count_total_words(text):
    """
    Count total meaningful words in text.

    Logic:
    - Only alphabetic words are counted
    - Numbers and symbols are ignored

    Example:
    "AI 2024 is great!" → ["AI", "is", "great"] → count = 3
    """

    # Find all words containing only letters
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    # Return total count
    return len(words)


def average_sentence_length(text):
    """
    Calculate average number of words per sentence.

    Formula:
    Average Sentence Length = Total Words / Number of Sentences
    """

    # Split text into sentences using punctuation
    sentences = re.split(r"[.!?]+", text)

    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    # If no valid sentences → return 0
    if not sentences:
        return 0

    # Count total words using previous function
    total_words = count_total_words(text)

    # Calculate average sentence length
    return round(total_words / len(sentences), 2)