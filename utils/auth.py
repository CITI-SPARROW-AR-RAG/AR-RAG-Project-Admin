import streamlit as st
import json
import os
import hashlib
import secrets
import string
from pathlib import Path

# Define the path to the users file
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"

# Ensure the data directory exists
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

def hash_password(password, salt=None):
    """Hash a password with a salt for secure storage"""
    if salt is None:
        # Generate a random salt
        alphabet = string.ascii_letters + string.digits
        salt = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    # Combine password and salt and hash
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def check_login(username, password):
    """Verify login credentials"""
    if not os.path.exists(USERS_FILE):
        # If no users file exists, create a default admin user for first-time setup
        create_initial_admin()
    
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username in users:
        stored_hash = users[username]['password_hash']
        salt = users[username]['salt']
        
        # Hash the provided password with the stored salt
        input_hash, _ = hash_password(password, salt)
        
        if input_hash == stored_hash:
            return True
    
    return False

def create_user(username, password, created_by):
    """Create a new admin user"""
    if not os.path.exists(USERS_FILE):
        users = {}
    else:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Hash the password
    password_hash, salt = hash_password(password)
    
    # Add the new user
    users[username] = {
        "password_hash": password_hash,
        "salt": salt,
        "created_by": created_by,
        "created_at": str(datetime.datetime.now())
    }
    
    # Save the updated users file
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return True, "User created successfully"

def create_initial_admin():
    """Create an initial admin user if no users exist"""
    # Default credentials - you should change these immediately after first login
    username = "admin"
    password = "admin"  # This is insecure - change after first login
    
    password_hash, salt = hash_password(password)
    
    users = {
        username: {
            "password_hash": password_hash,
            "salt": salt,
            "created_by": "system",
            "created_at": str(datetime.datetime.now())
        }
    }
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    
    # Save the users file
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return True

# Add missing import for datetime
import datetime