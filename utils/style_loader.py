import streamlit as st
from pathlib import Path


def load_css():
    """
    Load external CSS file and apply custom styling to Streamlit app.

    This allows us to:
    - Customize UI design
    - Improve look and feel
    - Override default Streamlit styles
    """

    # -------------------------------------------
    # GET PROJECT ROOT PATH
    # -------------------------------------------

    # Get absolute path of project root directory
    project_root = Path(__file__).resolve().parent.parent

    # -------------------------------------------
    # LOCATE CSS FILE
    # -------------------------------------------

    # Path to CSS file inside "styles" folder
    css_file = project_root / "styles" / "style.css"

    # -------------------------------------------
    # LOAD AND APPLY CSS
    # -------------------------------------------

    # Check if CSS file exists
    if css_file.exists():

        # Open CSS file in read mode
        with open(css_file, "r", encoding="utf-8") as f:

            # Inject CSS into Streamlit app using HTML <style> tag
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True  # allows custom HTML/CSS
            )