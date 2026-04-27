from datetime import datetime

import pandas as pd
import streamlit as st

# Custom styling for UI
from utils.style_loader import load_css

# MongoDB collection for storing feedback
from utils.db import feedback_collection


def show():
    # Load CSS styling
    load_css()

    # Page title
    st.title("💬 Feedback")

    # -------------------------------
    # LOGIN CHECK
    # -------------------------------
    # Ensure only logged-in users can submit feedback
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please login first.")
        st.stop()

    # Get username from session
    username = st.session_state.username
    st.write(f"**Logged in as:** {username}")

    # -------------------------------
    # FEEDBACK FORM
    # -------------------------------

    # Rating slider (1 to 5 stars)
    rating = st.slider("⭐ Rate the system", 1, 5, 3)

    # Main feedback input
    feedback_text = st.text_area("💬 Write your feedback")

    # Optional improvement suggestions
    improvements = st.text_area("🛠 Suggestions for improvement (optional)")

    # -------------------------------
    # SUBMIT BUTTON
    # -------------------------------
    if st.button("Submit Feedback"):

        # Validation: feedback should not be empty
        if feedback_text.strip() == "":
            st.error("❌ Please write feedback before submitting.")

        else:
            # Create feedback record
            feedback_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Current time
                "username": username,   # User who submitted
                "rating": rating,       # Rating (1–5)
                "feedback": feedback_text,   # Feedback message
                "improvements": improvements  # Optional suggestions
            }

            try:
                # Insert into MongoDB
                feedback_collection.insert_one(feedback_entry)

                st.success("✅ Feedback submitted successfully!")

            except Exception as e:
                # Handle database errors
                st.error(f"❌ Failed to save feedback: {e}")

    # -------------------------------
    # DISPLAY PREVIOUS FEEDBACK
    # -------------------------------
    st.subheader("📋 Previous Feedback")

    try:
        # Fetch all feedback records (exclude MongoDB _id)
        records = list(feedback_collection.find({}, {"_id": 0}))

    except Exception as e:
        st.error(f"❌ Failed to load feedback: {e}")
        return

    # If no feedback exists
    if not records:
        st.info("No feedback available yet.")

    else:
        # Convert records to DataFrame for table display
        df = pd.DataFrame(records)

        # Show feedback table
        st.dataframe(df, use_container_width=True)