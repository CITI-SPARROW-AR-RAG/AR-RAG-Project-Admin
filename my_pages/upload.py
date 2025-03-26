import streamlit as st
from utils.file_manager import save_uploaded_file

def show_upload_page():
    """Display the file upload page"""
    st.title("Upload Files")
    
    # File uploader widget
    uploaded_files = st.file_uploader(
        "Upload one or more files", 
        accept_multiple_files=True,
        type=None  # Accept all file types
    )
    
    # Vector DB option
    include_in_vector_db = st.checkbox("Include in Vector Database", value=False)
    
    # Upload button
    if st.button("Process Uploads") and uploaded_files:
        with st.spinner("Processing uploads..."):
            for uploaded_file in uploaded_files:
                # Process and save the file
                file_id, file_info = save_uploaded_file(uploaded_file, include_in_vector_db)
                
                # # If file should be included in vector DB, add it
                # if include_in_vector_db:
                #     from utils.vector_db import add_file_to_vector_db
                #     success, message = add_file_to_vector_db(file_id, file_info)
                #     if not success:
                #         st.warning(f"File uploaded but not added to vector DB: {message}")
                
                # Show success message
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    # Information section
    st.markdown("### Supported File Types")
    st.info("""
    You can upload various file types including:
    - Text files (.txt, .md)
    - Documents (.pdf, .doc, .docx)
    - Spreadsheets (.csv, .xls, .xlsx)
    - And more!
    
    Files marked for inclusion in the vector database will be processed and indexed.
    """)
    
    # File size limit information
    st.markdown("### File Size Limits")
    st.info("Maximum file size: 200 MB per file")