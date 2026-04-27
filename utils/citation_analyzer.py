import re


def analyze_citations(text):
    """
    Analyze and count different types of citations in research paper.

    This function detects:
    1. Numeric citations → [1], [2-5], [3,4]
    2. Author-year (parentheses) → (Smith, 2020)
    3. Author-year (inline) → Smith (2020)
    """

    # -----------------------------------
    # 1. Numeric citation style
    # Example: [1], [2,3], [4-7]
    # -----------------------------------
    square_bracket_citations = re.findall(
        r"\[(?:\d+(?:\s*[-,]\s*\d+)*)\]",
        text
    )

    # -----------------------------------
    # 2. Author-year citation (parentheses)
    # Example: (Smith, 2020), (Kumar et al., 2019)
    # -----------------------------------
    author_year_parentheses = re.findall(
        r"\([A-Z][A-Za-z]+(?:\s+et al\.)?,\s*\d{4}\)",
        text
    )

    # -----------------------------------
    # 3. Author-year citation (inline)
    # Example: Smith (2020), Kumar et al. (2019)
    # -----------------------------------
    author_year_inline = re.findall(
        r"[A-Z][A-Za-z]+(?:\s+et al\.)?\s*\(\d{4}\)",
        text
    )

    # -----------------------------------
    # TOTAL CITATION COUNT
    # -----------------------------------
    total = (
        len(square_bracket_citations)
        + len(author_year_parentheses)
        + len(author_year_inline)
    )

    # -----------------------------------
    # RETURN RESULT
    # -----------------------------------
    return {
        "count": total,   # Total citations
        "bracket_style": len(square_bracket_citations),   # [1], [2-3]
        "author_year_parentheses": len(author_year_parentheses),  # (Smith, 2020)
        "author_year_inline": len(author_year_inline)   # Smith (2020)
    }