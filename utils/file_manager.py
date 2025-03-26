import os
import streamlit as st
import shutil
import json
from pathlib import Path
import uuid
import datetime
import requests

# Define constants
FILES_DIR = Path(__file__).parent.parent / "data" / "files"
FILES_INDEX = Path(__file__).parent.parent / "data" / "files_index.json"

# Ensure directories exist
os.makedirs(FILES_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file, in_vector_db=False):
    API_URL = "http://127.0.0.1:8000/admin/upload_file"
    
    # Mengirim file sebagai multipart/form-data
    files = {"uploaded_file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    data = {
        "username": st.session_state.username,
        "in_vector_db": str(in_vector_db).lower(),  # FastAPI menerima string "true"/"false"
    }
    
    response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()["file_id"], response.json()["metadata"]
    else:
        return None, {"error": response.text}

def list_files():
    API_URL = "http://127.0.0.1:8000/admin/list_files"
    response = requests.get(API_URL)
    files_index = response.json()
    return files_index

def delete_file(file_id):
    """Delete a file and its metadata"""
    API_URL = "http://127.0.0.1:8000/admin/delete_file"
    response = requests.delete(API_URL, params={"file_id": file_id})

    if response.status_code != 200:
        return {"status": False, "message": "Server error"}

    return response.json()

def download_file(file_id):
    """Download file from server"""
    API_URL = "http://127.0.0.1:8000/admin/download_file"
    response = requests.get(API_URL, params={"file_id": file_id}, stream=True)

    if response.status_code != 200:
        return None, response.json().get("error", "Unknown error")

    file_data = response.content
    file_name = response.headers.get("Content-Disposition", "").split("filename=")[-1]

    return file_data, file_name 

def update_vector_db_status(file_id, in_vector_db):
    """Update whether a file is included in the vector database"""
    if not os.path.exists(FILES_INDEX):
        return False, "Files index not found"
    
    with open(FILES_INDEX, 'r') as f:
        files_index = json.load(f)
    
    if file_id not in files_index:
        return False, "File not found"
    
    # Update status
    files_index[file_id]["in_vector_db"] = in_vector_db
    
    # Save changes
    with open(FILES_INDEX, 'w') as f:
        json.dump(files_index, f, indent=4)
    
    return True, f"File vector DB status updated to: {in_vector_db}"

