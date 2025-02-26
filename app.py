import streamlit as st
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent / "my_pages"))

# Import utility modules
from utils.auth import check_login, hash_password
from utils.file_manager import list_files

# Configuration and session state initialization
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'login'

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
    
    # Header
    st.markdown("# Admin Interface")
    
    # Authentication check
    if not st.session_state.logged_in:
        from my_pages.login import show_login_page
        show_login_page()
        return
    
    # Sidebar navigation for logged-in users
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.username}**")
        
        st.subheader("Navigation")

        # Add "Change Password" to the pages list
        pages = ["Upload Files", "Files Dashboard", "Create Admin User", "RAG Evaluation", "Change Password"]

        # **Validasi active_page**
        if "active_page" not in st.session_state or st.session_state.active_page not in pages:
            st.session_state.active_page = pages[0]  # Default ke halaman pertama

        # Gunakan radio button dengan default dari session_state
        selected_page = st.radio(
            "Select a page:",
            pages,
            key="navigation",
            index=pages.index(st.session_state.active_page)  # Sekarang ini aman
        )

        # Update session state agar tetap diingat
        st.session_state.active_page = selected_page

        st.button("Logout", on_click=logout)

    # Page routing
    if st.session_state.active_page == "Upload Files":
        from my_pages.upload import show_upload_page
        show_upload_page()
    elif st.session_state.active_page == "Files Dashboard":
        from my_pages.files_dashboard import show_files_dashboard
        show_files_dashboard()
    elif st.session_state.active_page == "Create Admin User":
        from my_pages.signup import show_signup_page
        show_signup_page()
    elif st.session_state.active_page == "RAG Evaluation":
        from my_pages.evaluation import show_evaluation_page
        show_evaluation_page()
    elif st.session_state.active_page == "Change Password":
        from my_pages.change_password import show_change_password_page
        show_change_password_page()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.active_page = 'login'

if __name__ == "__main__":
    main()