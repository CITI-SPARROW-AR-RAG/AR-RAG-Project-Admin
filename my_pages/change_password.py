import streamlit as st
from utils.auth import check_login, hash_password
import json
from pathlib import Path
import os

# Define the path to the users file
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

def show_change_password_page():
    """Display the page to change the current user's password"""
    st.header("Change Your Password")
    
    # Get the logged-in username
    username = st.session_state.username

    # Ensure the users file exists
    if not os.path.exists(USERS_FILE):
        st.error("No users file found!")
        return
    
    # Load users from the file
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
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
        
        # Verify old password
        stored_hash = users[username]["password_hash"]
        salt = users[username]["salt"]
        old_hash, _ = hash_password(old_password, salt)

        if old_hash != stored_hash:
            st.error("Old password is incorrect.")
            return
        
        # Hash the new password
        new_hash, new_salt = hash_password(new_password)

        # Update the user's password
        users[username]["password_hash"] = new_hash
        users[username]["salt"] = new_salt

        # Save the updated users file
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        
        st.success("Password updated successfully!")
