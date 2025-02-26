import streamlit as st
from utils.auth import create_user

def show_signup_page():
    """Display the admin user creation page"""
    st.title("Create Admin User")
    
    with st.form("signup_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Create User")
        
        if submit:
            if not new_username or not new_password:
                st.error("Username and password are required")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = create_user(new_username, new_password, st.session_state.username)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    st.markdown("### Security Guidelines")
    st.info("""
    For secure passwords:
    - Use at least 12 characters
    - Include uppercase and lowercase letters, numbers, and special characters
    - Avoid common words or phrases
    - Do not reuse passwords from other sites
    """)