import os
import streamlit as st
import shutil
import json
from pathlib import Path
import uuid
import datetime

# Define constants
FILES_DIR = Path(__file__).parent.parent / "data" / "files"
FILES_INDEX = Path(__file__).parent.parent / "data" / "files_index.json"

# Ensure directories exist
os.makedirs(FILES_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file, in_vector_db=False):
    """Save an uploaded file and record its metadata"""
    if not os.path.exists(FILES_INDEX):
        with open(FILES_INDEX, 'w') as f:
            json.dump({}, f)
    
    # Generate a unique ID for the file
    file_id = str(uuid.uuid4())
    
    # Extract file extension
    original_filename = uploaded_file.name
    ext = os.path.splitext(original_filename)[1]
    
    # Create a unique filename with the original extension
    filename = f"{file_id}{ext}"
    file_path = os.path.join(FILES_DIR, filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Record metadata
    with open(FILES_INDEX, 'r') as f:
        files_index = json.load(f)
    
    files_index[file_id] = {
        "original_filename": original_filename,
        "stored_filename": filename,
        "upload_time": str(datetime.datetime.now()),
        "uploader": st.session_state.username,
        "file_size_bytes": file_size,
        "file_type": uploaded_file.type,
        "in_vector_db": in_vector_db,
        "path": file_path
    }
    
    with open(FILES_INDEX, 'w') as f:
        json.dump(files_index, f, indent=4)
    
    return file_id, files_index[file_id]

def list_files():
    """Get a list of all uploaded files with their metadata"""
    if not os.path.exists(FILES_INDEX):
        return {}
    
    with open(FILES_INDEX, 'r') as f:
        files_index = json.load(f)
    
    return files_index

def get_file_metadata(file_id):
    """Get metadata for a specific file"""
    if not os.path.exists(FILES_INDEX):
        return None
    
    with open(FILES_INDEX, 'r') as f:
        files_index = json.load(f)
    
    return files_index.get(file_id)

def delete_file(file_id):
    """Delete a file and its metadata"""
    if not os.path.exists(FILES_INDEX):
        return False, "Files index not found"
    
    with open(FILES_INDEX, 'r') as f:
        files_index = json.load(f)
    
    if file_id not in files_index:
        return False, "File not found"
    
    # Get the file info
    file_info = files_index[file_id]
    file_path = os.path.join(FILES_DIR, file_info["stored_filename"])
    
    # Delete the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from index
    del files_index[file_id]
    
    # Update index file
    with open(FILES_INDEX, 'w') as f:
        json.dump(files_index, f, indent=4)
    
    return True, "File deleted successfully"

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

def download_file(file_id):
    """Get file data for download"""
    file_metadata = get_file_metadata(file_id)
    if not file_metadata:
        return None, "File not found"
    
    file_path = os.path.join(FILES_DIR, file_metadata["stored_filename"])
    
    if not os.path.exists(file_path):
        return None, "File data not found"
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    return file_data, file_metadata["original_filename"]