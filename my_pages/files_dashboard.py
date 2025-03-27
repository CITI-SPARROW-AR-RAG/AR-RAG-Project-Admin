import streamlit as st
import pandas as pd
from utils.file_manager import list_files, delete_file, download_file, add_file_to_vector_db, remove_file_from_vector_db

def show_files_dashboard():
    """Display the files dashboard"""
    st.title("Files Dashboard")
    
    # Get list of files
    files = list_files()
    
    if not files:
        st.info("No files have been uploaded yet.")
        return
    
    # Create a dataframe for display
    files_data = []
    for file_id, file_info in files.items():
        files_data.append({
            "ID": file_id,
            "Filename": file_info["original_filename"],
            "Type": file_info["file_type"],
            "Size (KB)": round(file_info["file_size_bytes"] / 1024, 2),
            "Upload Date": file_info["upload_time"],
            "Uploader": file_info["uploader"],
            "In Vector DB": file_info["in_vector_db"]
        })
    
    df = pd.DataFrame(files_data)
    
    # Add search/filter functionality
    search_term = st.text_input("Search files by name:")
    if search_term:
        df = df[df["Filename"].str.contains(search_term, case=False)]
    
    # File type filter
    if len(df) > 0:
        file_types = ["All"] + sorted(df["Type"].unique().tolist())
        selected_type = st.selectbox("Filter by file type:", file_types)
        if selected_type != "All":
            df = df[df["Type"] == selected_type]
    
    # Vector DB filter
    vector_db_filter = st.radio(
        "Vector Database Status:",
        ["All", "In Vector DB", "Not in Vector DB"],
        horizontal=True
    )
    
    if vector_db_filter == "In Vector DB":
        df = df[df["In Vector DB"] == True]
    elif vector_db_filter == "Not in Vector DB":
        df = df[df["In Vector DB"] == False]
    
    # Display the dataframe
    st.dataframe(df)
    
    # File actions
    st.subheader("File Actions")
    
    # Select a file
    file_ids = df["ID"].tolist()
    file_names = df["Filename"].tolist()
    
    if not file_ids:
        st.info("No files match your filter criteria.")
        return
    
    # Create a dropdown with file names but store the IDs
    selected_index = st.selectbox(
        "Select a file:",
        range(len(file_ids)),
        format_func=lambda i: file_names[i]
    )
    
    selected_file_id = file_ids[selected_index]
    selected_file_info = files[selected_file_id]
    
    # Show file details
    st.json(selected_file_info)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download button
        if st.button("Download File"):
            file_data, filename = download_file(selected_file_id)
            if file_data:
                st.download_button(
                    label="Click to download",
                    data=file_data,
                    file_name=filename,
                    mime=selected_file_info["file_type"]
                )
            else:
                st.error("File could not be downloaded")
    
    with col2:
        if st.button("Delete File"):
            if st.session_state.get("confirm_delete") != selected_file_id:
                st.session_state.confirm_delete = selected_file_id
                st.warning(f"Are you sure you want to delete '{selected_file_info['original_filename']}'? Click Delete again to confirm.")
            else:
                response = delete_file(selected_file_id) 
                result = remove_file_from_vector_db(selected_file_id)

                if response["status"] and result['status']:
                    st.success(response["message"])
                    st.session_state.confirm_delete = None
                    st.rerun()
                else:
                    st.error(response["message"])

    
    with col3:
        current_status = selected_file_info.get("in_vector_db", False)
        new_status = not current_status
        action = "Add to" if new_status else "Remove from"

        if st.button(f"{action} Vector DB"):
            with st.spinner(f"{action} Vector DB... Please wait."):
                try:
                    if new_status:
                        # Add file to vector database
                        result = add_file_to_vector_db(selected_file_id, selected_file_info)
                    else:
                        # Remove file from vector database
                        result = remove_file_from_vector_db(selected_file_id)

                    if result['status']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
