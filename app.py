import streamlit as st

# Import page modules
import pages.analyzer as analyzer
import pages.dashboard as dashboard
import pages.feedback as feedback

# Import CSS loader
from utils.style_loader import load_css


# -------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------

st.set_page_config(
    page_title="Academic Research Paper Analyzer",  # Browser tab title
    page_icon="📚",                                 # Icon
    layout="wide"                                   # Full-width layout
)

# Load custom CSS
load_css()


# -------------------------------------------
# HIDE DEFAULT SIDEBAR NAVIGATION
# -------------------------------------------

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------

# Track login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Store username
if "username" not in st.session_state:
    st.session_state.username = ""

# Track current page (navigation control)
if "page" not in st.session_state:
    st.session_state.page = "login"


# -------------------------------------------
# LOGIN PAGE
# -------------------------------------------

if st.session_state.page == "login":

    st.title("🔐 Login")
    st.markdown("### Academic Research Paper Analyzer")

    # User input fields
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    # Login button
    if st.button("Login"):

        # Simple validation (no database auth)
        if username.strip() and password.strip():
            st.session_state.logged_in = True
            st.session_state.username = username

            # Navigate to analyzer page
            st.session_state.page = "analyzer"
            st.rerun()

        else:
            st.error("❌ Please enter both username and password.")


# -------------------------------------------
# ANALYZER PAGE
# -------------------------------------------

elif st.session_state.page == "analyzer":

    # Show analyzer page
    analyzer.show()

    st.markdown("---")

    # Navigation button → Dashboard
    if st.button("Next ➡ Go to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


# -------------------------------------------
# DASHBOARD PAGE
# -------------------------------------------

elif st.session_state.page == "dashboard":

    # Show dashboard page
    dashboard.show()

    st.markdown("---")

    # Create two columns for navigation buttons
    col1, col2 = st.columns(2)

    with col1:
        # Back button → Analyzer
        if st.button("⬅ Back to Analyzer"):
            st.session_state.page = "analyzer"
            st.rerun()

    with col2:
        # Next button → Feedback
        if st.button("Next ➡ Go to Feedback"):
            st.session_state.page = "feedback"
            st.rerun()


# -------------------------------------------
# FEEDBACK PAGE
# -------------------------------------------

elif st.session_state.page == "feedback":

    # Show feedback page
    feedback.show()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Back button → Dashboard
        if st.button("⬅ Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

    with col2:
        # Reset app → Logout + go to login page
        if st.button("🔄 Reset App"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "login"
            st.rerun()