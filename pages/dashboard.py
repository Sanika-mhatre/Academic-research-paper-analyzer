import pandas as pd
import plotly.express as px
import streamlit as st

from utils.style_loader import load_css
from utils.db import dashboard_collection


def normalize_score(value):
    """
    Converts score into percentage format.

    Some values like novelty and clarity may be stored as:
    0.70 meaning 70%

    Some values may already be:
    70 meaning 70%

    This function handles both safely.
    """

    try:
        value = float(value)
    except Exception:
        return 0

    if value <= 1:
        return value * 100

    return value


def calculate_readiness_score(row):
    """
    Calculates overall paper readiness percentage.

    Higher values are good for:
    - novelty
    - clarity
    - grammar accuracy
    - readability
    - citation strength

    Lower value is good for:
    - plagiarism

    Final score is calculated out of 100.
    """

    novelty = normalize_score(row.get("novelty", 0))
    clarity = normalize_score(row.get("clarity", 0))
    grammar = normalize_score(row.get("grammar_accuracy", 0))

    readability = row.get("readability", 0)
    readability = max(0, min(float(readability), 100)) if pd.notna(readability) else 0

    citation_strength = row.get("citation_strength", 0)
    citation_strength = max(0, min(float(citation_strength), 10)) * 10 if pd.notna(citation_strength) else 0

    plagiarism_percent = row.get("plagiarism_percent", 0)
    plagiarism_percent = max(0, min(float(plagiarism_percent), 100)) if pd.notna(plagiarism_percent) else 0

    originality = 100 - plagiarism_percent

    readiness = (
        novelty +
        clarity +
        grammar +
        readability +
        citation_strength +
        originality
    ) / 6

    return round(readiness, 2)


def get_readiness_status(score):
    """
    Converts readiness percentage into final status.
    """

    if score >= 95:
        return "Perfect"
    elif score >= 70:
        return "Good to Go"
    else:
        return "Need Improvement"


def show():
    load_css()

    st.title("📊 Dashboard")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please login first.")
        st.stop()

    try:
        records = list(dashboard_collection.find({}, {"_id": 0}))
    except Exception as e:
        st.error(f"❌ Failed to load dashboard data: {e}")
        return

    if not records:
        st.warning("⚠️ No analysis data found. Please analyze and save a paper first.")
        return

    df = pd.DataFrame(records)

    numeric_cols = [
        "novelty",
        "clarity",
        "readability",
        "citation_strength",
        "plagiarism_percent",
        "grammar_accuracy",
        "grammar_errors",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if df.empty:
        st.warning("⚠️ No valid dashboard data found.")
        return

    # Calculate readiness percentage for every saved paper
    df["readiness_score"] = df.apply(calculate_readiness_score, axis=1)

    # Assign status based on readiness score
    df["readiness_status"] = df["readiness_score"].apply(get_readiness_status)

    latest_row = df.iloc[-1]

    latest_readiness = latest_row["readiness_score"]
    latest_status = latest_row["readiness_status"]
    need_improvement_percent = round(100 - latest_readiness, 2)

    st.success("✅ Dashboard data loaded successfully!")

    # ---------------------------------------------------
    # Overview metrics
    # ---------------------------------------------------
    st.subheader("📌 Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Papers", len(df))
    c2.metric("Avg Novelty", f"{df['novelty'].mean():.2f}")
    c3.metric("Avg Clarity", f"{df['clarity'].mean():.2f}")
    c4.metric("Avg Readiness", f"{df['readiness_score'].mean():.2f}%")

    # ---------------------------------------------------
    # Bar chart
    # ---------------------------------------------------
    st.subheader("📈 Paper Score Comparison")

    chart_df = df.copy()

    # Convert novelty and clarity into percentage for better chart display
    chart_df["novelty_percent"] = chart_df["novelty"].apply(normalize_score)
    chart_df["clarity_percent"] = chart_df["clarity"].apply(normalize_score)

    fig_bar = px.bar(
        chart_df,
        x="filename",
        y=["novelty_percent", "clarity_percent", "readiness_score"],
        barmode="group",
        title="Novelty, Clarity and Readiness per Paper",
        labels={
            "value": "Percentage",
            "filename": "Paper",
            "variable": "Metric",
        },
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------------------------------
    # Overall Paper Readiness Pie Chart
    # ---------------------------------------------------
    st.subheader("🧠 Overall Paper Readiness")

    st.metric("Overall Paper Readiness", f"{latest_readiness}%")
    st.write(f"**Status:** {latest_status}")

    if latest_status == "Perfect":
        pie_df = pd.DataFrame({
            "Category": ["Perfect", "Need Improvement"],
            "Percentage": [latest_readiness, need_improvement_percent],
        })
    else:
        pie_df = pd.DataFrame({
            "Category": ["Good to Go", "Need Improvement"],
            "Percentage": [latest_readiness, need_improvement_percent],
        })

    fig_pie = px.pie(
        pie_df,
        names="Category",
        values="Percentage",
        title="Latest Paper Readiness Percentage",
        hole=0.35,
    )

    fig_pie.update_traces(
        textinfo="label+percent+value",
        textposition="inside"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    p1, p2 = st.columns(2)

    if latest_status == "Perfect":
        p1.metric("Perfect %", f"{latest_readiness}%")
    else:
        p1.metric("Good to Go %", f"{latest_readiness}%")

    p2.metric("Need Improvement %", f"{need_improvement_percent}%")

    if latest_status == "Perfect":
        st.success("🌟 Perfect! This paper is excellent and ready.")
    elif latest_status == "Good to Go":
        st.info("✅ Good to go. Only minor improvements may be needed.")
    else:
        st.warning("⚠️ This paper needs improvement before final submission.")

    # ---------------------------------------------------
    # Improvement suggestions for latest paper
    # ---------------------------------------------------
    st.subheader("📋 What Should Be Improved?")

    novelty_percent = normalize_score(latest_row.get("novelty", 0))
    clarity_percent = normalize_score(latest_row.get("clarity", 0))
    grammar_accuracy = normalize_score(latest_row.get("grammar_accuracy", 0))
    readability = latest_row.get("readability", 0)
    citation_strength = latest_row.get("citation_strength", 0)
    plagiarism_percent = latest_row.get("plagiarism_percent", 0)

    has_suggestion = False

    if novelty_percent < 70:
        st.warning("💡 Novelty should be improved. Add more original contribution or stronger ideas.")
        has_suggestion = True

    if clarity_percent < 70:
        st.warning("✏️ Clarity should be improved. Use clearer and better-structured writing.")
        has_suggestion = True

    if grammar_accuracy < 90:
        st.warning("📝 Grammar should be improved. Fix punctuation, spelling, and sentence formation issues.")
        has_suggestion = True

    if readability < 50:
        st.warning("📚 Readability should be improved. Use simpler and more understandable sentences.")
        has_suggestion = True

    if citation_strength < 5:
        st.warning("📖 Citation strength should be improved. Add more academic citations in proper format.")
        has_suggestion = True

    if plagiarism_percent > 15:
        st.warning("⚠️ Originality should be improved. Reduce copied or repeated content.")
        has_suggestion = True

    if not has_suggestion:
        st.success("✅ No major improvement required. This paper looks ready.")

    # ---------------------------------------------------
    # Latest paper summary
    # ---------------------------------------------------
    st.subheader("🕒 Latest Paper Summary")

    st.write(f"**Paper:** {latest_row.get('filename', 'N/A')}")
    st.write(f"**Novelty:** {latest_row.get('novelty', 0)}")
    st.write(f"**Clarity:** {latest_row.get('clarity', 0)}")
    st.write(f"**Readability:** {latest_row.get('readability', 0)}")
    st.write(f"**Citation Strength:** {latest_row.get('citation_strength', 0)}")
    st.write(f"**Grammar Accuracy:** {latest_row.get('grammar_accuracy', 0)}%")
    st.write(f"**Plagiarism Percent:** {latest_row.get('plagiarism_percent', 0)}%")
    st.write(f"**Overall Readiness:** {latest_readiness}%")
    st.write(f"**Status:** {latest_status}")
    st.write(f"**Keywords:** {latest_row.get('keywords', 'N/A')}")

    # ---------------------------------------------------
    # Analysis table
    # ---------------------------------------------------
    st.subheader("🗂 Analysis Table")

    display_cols = [
        "timestamp",
        "username",
        "filename",
        "novelty",
        "clarity",
        "readability",
        "citation_strength",
        "grammar_accuracy",
        "plagiarism_percent",
        "readiness_score",
        "readiness_status",
    ]

    display_cols = [col for col in display_cols if col in df.columns]

    st.dataframe(df[display_cols], use_container_width=True)