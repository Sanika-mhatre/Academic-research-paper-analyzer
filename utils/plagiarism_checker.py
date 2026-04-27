import re
from pathlib import Path

# NLP tools for similarity calculation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text):
    """
    Clean raw extracted text from PDF.

    - Convert to lowercase
    - Fix broken words (e.g., "cita- tions" → "citations")
    - Remove extra spaces
    - Keep only useful characters
    """

    text = text.lower()

    # Fix broken words caused by PDF extraction
    text = re.sub(r"-\s+", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted symbols but keep sentence punctuation
    text = re.sub(r"[^a-z0-9\s.!?]", "", text)

    return text.strip()


def split_sentences(text):
    """
    Split text into meaningful sentences.

    - Uses punctuation (., !, ?)
    - Removes very short sentences (noise)
    """

    text = clean_text(text)

    # Split sentences using punctuation
    sentences = re.split(r"[.!?]+", text)

    final_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()
        words = sentence.split()

        # Keep only meaningful sentences (at least 5 words)
        if len(words) >= 5:
            final_sentences.append(sentence)

    return final_sentences


def load_corpus():
    """
    Load reference documents (corpus).

    This is used for external plagiarism detection.
    """

    base_dir = Path(__file__).resolve().parent.parent

    # Folder containing multiple text files
    corpus_folder = base_dir / "data" / "corpus"

    # Backup single corpus file
    old_corpus_file = base_dir / "data" / "corpus_samples.txt"

    corpus_texts = []

    # Load all .txt files from corpus folder
    if corpus_folder.exists():
        for file in corpus_folder.glob("*.txt"):
            try:
                corpus_texts.append(file.read_text(encoding="utf-8"))
            except Exception:
                pass

    # Load fallback file
    if old_corpus_file.exists():
        try:
            corpus_texts.append(old_corpus_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    return corpus_texts


def detect_internal_plagiarism(user_sentences, threshold=0.50):
    """
    Detect repeated or similar sentences INSIDE the same paper.

    Example:
    If sentence appears multiple times → internal plagiarism.
    """

    matches = []
    matched_indexes = set()

    # If too few sentences, skip
    if len(user_sentences) < 2:
        return matches, matched_indexes

    # Convert sentences into TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(user_sentences)

    # Compute similarity between sentences
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Compare each sentence with others
    for i in range(len(user_sentences)):
        for j in range(i + 1, len(user_sentences)):

            similarity = similarity_matrix[i][j]

            # If similarity above threshold → mark as plagiarism
            if similarity >= threshold:
                matched_indexes.add(i)
                matched_indexes.add(j)

                matches.append({
                    "type": "Internal Repetition",
                    "uploaded_sentence": user_sentences[i],
                    "matched_sentence": user_sentences[j],
                    "similarity": round(float(similarity) * 100, 2)
                })

    return matches, matched_indexes


def detect_external_plagiarism(user_sentences, threshold=0.55):
    """
    Detect plagiarism by comparing user text with corpus (external data).
    """

    matches = []
    matched_indexes = set()

    # Load corpus data
    corpus_texts = load_corpus()

    if not corpus_texts:
        return matches, matched_indexes

    corpus_sentences = []

    # Split all corpus text into sentences
    for corpus_text in corpus_texts:
        corpus_sentences.extend(split_sentences(corpus_text))

    if not corpus_sentences:
        return matches, matched_indexes

    # Combine user + corpus sentences
    all_sentences = user_sentences + corpus_sentences

    # Convert to TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    # Separate user and corpus vectors
    user_matrix = tfidf_matrix[:len(user_sentences)]
    corpus_matrix = tfidf_matrix[len(user_sentences):]

    # Compute similarity
    similarity_matrix = cosine_similarity(user_matrix, corpus_matrix)

    for i, scores in enumerate(similarity_matrix):

        best_score = scores.max()
        best_index = scores.argmax()

        # If similarity above threshold → plagiarism detected
        if best_score >= threshold:
            matched_indexes.add(i)

            matches.append({
                "type": "External Corpus Match",
                "uploaded_sentence": user_sentences[i],
                "matched_sentence": corpus_sentences[best_index],
                "similarity": round(float(best_score) * 100, 2)
            })

    return matches, matched_indexes


def check_plagiarism(text):
    """
    MAIN FUNCTION

    Performs:
    1. Internal plagiarism detection (self-repetition)
    2. External plagiarism detection (corpus comparison)
    """

    # Convert text into sentences
    user_sentences = split_sentences(text)

    # If no valid sentences
    if not user_sentences:
        return {
            "score": 0.0,
            "matches": [],
            "total_sentences": 0,
            "matched_sentences": 0,
            "message": "Not enough text found for plagiarism checking."
        }

    # Detect internal plagiarism
    internal_matches, internal_indexes = detect_internal_plagiarism(user_sentences)

    # Detect external plagiarism
    external_matches, external_indexes = detect_external_plagiarism(user_sentences)

    # Combine both results
    all_indexes = internal_indexes.union(external_indexes)
    all_matches = internal_matches + external_matches

    # Calculate plagiarism percentage
    plagiarism_score = (len(all_indexes) / len(user_sentences)) * 100

    return {
        "score": round(plagiarism_score, 2),
        "matches": all_matches[:15],  # limit output
        "total_sentences": len(user_sentences),
        "matched_sentences": len(all_indexes),
        "message": "Local plagiarism check completed using internal and external similarity detection."
    }