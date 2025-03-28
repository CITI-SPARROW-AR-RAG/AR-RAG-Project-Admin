import streamlit as st
import json
from pathlib import Path
import os, requests

# Define the path to the users file
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

def show_change_password_page():
    """Display the page to change the current user's password"""
    st.header("Change Your Password")
    
    # Get the logged-in username
    username = st.session_state.username
    
    # Load users from the file
    API_URL = "http://127.0.0.1:8000/admin/get_users"
    response = requests.get(API_URL)
    users = response.json()
    
    if username not in users:
        st.error("User does not exist!")
        return
    
    # Form to change password
    with st.form("password_change_form"):
        old_password = st.text_input("Old Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit_button = st.form_submit_button("Change Password")
    
    if submit_button:
        if new_password != confirm_password:
            st.error("New password and confirmation do not match.")
            return
        
        API_URL = "http://127.0.0.1:8000/admin/verify_password"
        response = requests.get(API_URL, params={"username": username, "pass_input": old_password})
        response = response.json()

        if not response['verified']:
            st.error("Old password is incorrect.")
            return
        
        API_URL = "http://127.0.0.1:8000/admin/change_password"
        flag = requests.put(API_URL, params={"username": username, "new_password": new_password})

        st.success("Password updated successfully!")