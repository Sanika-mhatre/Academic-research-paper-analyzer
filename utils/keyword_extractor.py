import re
from collections import Counter

def extract_keywords(text, num_keywords=10):
    # Lowercase and remove punctuation
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)

    # Common stopwords to exclude
    stop_words = {
        'the', 'is', 'in', 'and', 'to', 'of', 'a', 'that', 'for', 'on', 'with',
        'as', 'by', 'this', 'an', 'are', 'at', 'be', 'from', 'or', 'which',
        'it', 'we', 'can', 'not', 'have', 'has', 'our', 'but', 'their'
    }

    # Remove stopwords
    keywords = [word for word in words if word not in stop_words]

    # Count and return top keywords
    freq = Counter(keywords)
    return [word for word, count in freq.most_common(num_keywords)]
