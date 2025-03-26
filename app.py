import streamlit as st
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent / "my_pages"))

# Import utility modules
from utils.file_manager import list_files

# Import all pages at the top to avoid conditional imports
from my_pages.signup import show_signup_page
from my_pages.login import show_login_page
from my_pages.upload import show_upload_page
from my_pages.files_dashboard import show_files_dashboard
from my_pages.evaluation import show_evaluation_page
from my_pages.change_password import show_change_password_page

# Configuration and session state initialization
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'login'

def logout():
    """Handles logout and resets session state."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.active_page = 'login'
    st.rerun()

def main():
    # Initialize session state
    init_session_state()
    
    # Set page config
    st.set_page_config(
        page_title="Admin Interface",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Authentication check
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Sidebar navigation for logged-in users
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.username}**")
        
        st.subheader("Navigation")

        # List of pages
        pages = ["Upload Files", "Files Dashboard", "RAG Evaluation", "Create Admin User", "Change Password"]

        # Validate active_page
        if "active_page" not in st.session_state or st.session_state.active_page not in pages:
            st.session_state.active_page = pages[0]  # Default to first page

        # Navigation radio button
        selected_page = st.radio(
            "Select a page:",
            pages,
            key="navigation",
            index=pages.index(st.session_state.active_page)
        )

        # If the selected page is different, update and rerun
        if selected_page != st.session_state.active_page:
            st.session_state.active_page = selected_page
            st.rerun()  # Force immediate rerun

        # Logout button
        if st.sidebar.button("Logout"):
            logout()

    # Page routing using pre-imported modules
    if st.session_state.active_page == "Upload Files":
        show_upload_page()
    elif st.session_state.active_page == "Files Dashboard":
        show_files_dashboard()
    elif st.session_state.active_page == "RAG Evaluation":
        show_evaluation_page()
    elif st.session_state.active_page == "Create Admin User":
        show_signup_page()
    elif st.session_state.active_page == "Change Password":
        show_change_password_page()

if __name__ == "__main__":
    main()
