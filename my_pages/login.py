import streamlit as st
from utils.auth import check_login

def show_login_page():
    """Display the login page"""
    st.title("Admin Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.info("Note: If this is your first time running the application, use 'admin' for both username and password, then change them immediately.")