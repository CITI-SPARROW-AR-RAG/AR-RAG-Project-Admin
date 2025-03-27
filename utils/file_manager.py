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

def add_file_to_vector_db(file_id, file_metadata):
    API_URL = "http://127.0.0.1:8000/admin/add_file_to_vdb"
    
    # Convert file_metadata to JSON string
    payload = {
        "file_id": file_id,
        "file_metadata": json.dumps(file_metadata)
    }
    
    # Send request to FastAPI server using form data
    response = requests.post(API_URL, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"status": False, "message": f"Error: {response.status_code}"}

def remove_file_from_vector_db(file_id):
    API_URL = "http://127.0.0.1:8000/admin/remove_file_from_vdb"

    response = requests.post(API_URL, data={"file_id": file_id})

    if response.status_code == 200:
        return response.json()
    else:
        return {"status": False, "message": f"Error: {response.status_code} - {response.text}"}