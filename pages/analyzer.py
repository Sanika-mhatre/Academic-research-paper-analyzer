import re
import concurrent.futures
from datetime import datetime

import streamlit as st
import textstat

# Importing utility functions (modular structure - very good practice)
from utils.style_loader import load_css
from utils.pdf_utils import extract_text_from_pdf
from utils.structure_predictor import predict_scores   # ML model (novelty, clarity)
from utils.grammar_checker import grammar_check
from utils.plagiarism_checker import check_plagiarism
from utils.copyleaks_checker import submit_to_copyleaks
from utils.citation_analyzer import analyze_citations
from utils.keyword_extractor import extract_keywords
from utils.db import analysis_collection, dashboard_collection
from utils.text_analyzer import (
    clean_extracted_text,
    count_total_words,
    average_sentence_length,
)


def extract_model_features(text):
    """
    Extract numerical features from the research paper.
    These features are used for:
    1. Displaying paper details
    2. Feeding ML model for prediction
    """

    # Clean text (remove noise, fix broken words)
    cleaned_text = clean_extracted_text(text)

    # Extract citation count
    citation_info = analyze_citations(cleaned_text)
    num_citations = citation_info.get("count", 0)

    # Count figures using regex
    num_figures = len(
        re.findall(r"\b(fig\.?|figure)\b", cleaned_text, flags=re.IGNORECASE)
    )

    # Count equations using simple pattern (x = something)
    num_equations = len(
        re.findall(r"\b[A-Za-z]+\s*=\s*[^.\n]+", cleaned_text)
    )

    # Count total words
    total_words = count_total_words(cleaned_text)

    # Calculate average sentence length
    avg_sentence_length = average_sentence_length(cleaned_text)

    return {
        "num_citations": num_citations,
        "num_figures": num_figures,
        "num_equations": num_equations,
        "total_words": total_words,
        "avg_sentence_length": avg_sentence_length,
    }


def show():
    # Load custom CSS for styling
    load_css()

    st.title("📄 Paper Analyzer")

    # Check if user is logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please login first.")
        st.stop()

    username = st.session_state.username
    st.write(f"**Logged in as:** {username}")

    # User input fields
    paper_name = st.text_input("📘 Enter Research Paper Title")
    uploaded_file = st.file_uploader(
        "📎 Upload PDF",
        type=["pdf"],
        key="analyzer_uploader"
    )

    # Run analysis only if file + title is provided
    if uploaded_file and paper_name.strip():

        with st.spinner("Analyzing paper..."):

            # Extract text from PDF
            raw_text = extract_text_from_pdf(uploaded_file)

            # Handle extraction failure
            if not raw_text or str(raw_text).startswith("Error"):
                st.error("❌ Could not extract text from PDF.")
                return

            # Clean text for further processing
            text = clean_extracted_text(raw_text)

            # Limit text length for performance optimization
            analysis_text = text[:8000]
            grammar_text = text[:3000]
            plagiarism_text = text[:5000]

            # Extract features
            features = extract_model_features(analysis_text)

            # Readability using Flesch score
            readability_score = round(
                textstat.flesch_reading_ease(analysis_text),
                2
            )

            # Extract keywords
            try:
                keywords = extract_keywords(analysis_text, num_keywords=10)
            except Exception:
                keywords = []

            # Run ML model (novelty + clarity)
            def run_structure():
                return predict_scores(features)

            # Run grammar checker
            def run_grammar():
                return grammar_check(grammar_text)

            # Run plagiarism checker + Copyleaks API
            def run_plagiarism():
                local_result = check_plagiarism(plagiarism_text)
                copyleaks_result = submit_to_copyleaks(plagiarism_text)

                return {
                    "local": local_result,
                    "copyleaks": copyleaks_result,
                }

            # Run all processes in parallel (fast execution)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                f1 = executor.submit(run_structure)
                f2 = executor.submit(run_grammar)
                f3 = executor.submit(run_plagiarism)

                structure_result = f1.result()
                grammar_result = f2.result()
                plagiarism_result = f3.result()

        # Extract ML outputs
        novelty_score, clarity_score = structure_result
        citation_count = features["num_citations"]

        # Calculate citation strength (rule-based)
        if citation_count >= 15:
            citation_strength = 9
        elif citation_count >= 10:
            citation_strength = 7
        elif citation_count >= 5:
            citation_strength = 5
        elif citation_count >= 1:
            citation_strength = 3
        else:
            citation_strength = 1

        # Extract plagiarism results
        local_plagiarism = plagiarism_result.get("local", {})
        copyleaks_result = plagiarism_result.get("copyleaks", {})

        plagiarism_percent = local_plagiarism.get("score", 0)
        matched_sentences = local_plagiarism.get("matches", [])

        # -------------------------------
        # DISPLAY SECTION
        # -------------------------------

        st.subheader("📋 Paper Details")
        st.write(f"**Paper Name:** {paper_name}")
        st.write(f"**Total Words Analyzed:** {features['total_words']}")
        st.write(f"**Detected Citations:** {features['num_citations']}")
        st.write(f"**Detected Figures:** {features['num_figures']}")
        st.write(f"**Detected Equations:** {features['num_equations']}")
        st.write(f"**Average Sentence Length:** {features['avg_sentence_length']}")
        st.write(f"**Readability Score:** {readability_score}")

        st.subheader("📊 Trained Model Output")
        col1, col2, col3 = st.columns(3)
        col1.metric("Novelty Score", novelty_score)
        col2.metric("Clarity Score", clarity_score)
        col3.metric("Citation Strength", citation_strength)

        st.subheader("🔑 Extracted Keywords")
        st.write(", ".join(keywords) if keywords else "No keywords found")

        # -------------------------------
        # GRAMMAR CHECK
        # -------------------------------
        st.subheader("📝 Grammar Check")

        if isinstance(grammar_result, dict):
            g1, g2 = st.columns(2)
            g1.metric("Grammar Accuracy", f"{grammar_result.get('accuracy', 0)}%")
            g2.metric("Grammar Issues", grammar_result.get("total_issues", 0))

            suggestions = grammar_result.get("suggestions", [])

            if not suggestions:
                st.success("✅ No major grammar issues found.")
            else:
                st.write("**Grammar Suggestions:**")

                for item in suggestions[:10]:
                    st.error(f"**Mistake:** {item.get('mistake', '')}")
                    st.info(f"**Issue:** {item.get('message', '')}")
                    st.success(f"**Suggestion:** {item.get('correction', '')}")
        else:
            st.write(grammar_result)

        # -------------------------------
        # PLAGIARISM CHECK
        # -------------------------------
        st.subheader("🔍 Plagiarism Check")

        st.metric("Local Plagiarism", f"{plagiarism_percent:.2f}%")

        if plagiarism_percent == 0:
            st.success("✅ No local plagiarism detected.")
        else:
            st.warning(f"⚠️ {plagiarism_percent:.2f}% local plagiarism detected.")

            st.write("**Matched Sentences:**")

            for match in matched_sentences[:10]:
                st.markdown(f"**Similarity:** {match.get('similarity', 0)}%")
                st.warning(f"Uploaded: {match.get('uploaded_sentence', '')}")
                st.info(f"Matched: {match.get('matched_sentence', '')}")
                st.divider()

        # -------------------------------
        # COPYLEAKS API
        # -------------------------------
        st.markdown("### 🌐 Copyleaks Scan")

        status = copyleaks_result.get("status", "unknown")
        message = copyleaks_result.get("message", "No Copyleaks response")
        scan_id = copyleaks_result.get("scan_id")

        st.info(message)

        if scan_id:
            st.write(f"**Scan ID:** {scan_id}")

        st.caption("Copyleaks scan is asynchronous. This ID is used to track results.")

        # -------------------------------
        # SAVE TO DATABASE
        # -------------------------------
        if st.button("💾 Save Analysis"):

            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "username": username,
                "filename": paper_name,
                "novelty": novelty_score,
                "clarity": clarity_score,
                "readability": readability_score,
                "keywords": ", ".join(keywords),
                "citation_strength": citation_strength,
                "plagiarism_percent": plagiarism_percent,
                "grammar_accuracy": grammar_result.get("accuracy", 0),
                "grammar_errors": grammar_result.get("total_issues", 0),
                "copyleaks_status": status,
                "copyleaks_scan_id": scan_id,
            }

            try:
                dashboard_collection.insert_one(log_entry)
                analysis_collection.insert_one(log_entry)
                st.success("✅ Analysis saved successfully!")
            except Exception as e:
                st.error(f"❌ Failed to save: {e}")

    else:
        st.info("Please enter paper title and upload a PDF.")