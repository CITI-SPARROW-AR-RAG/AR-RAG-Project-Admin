import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import glob, os
from datetime import datetime
from utils.rag_evaluator import run_evaluation, list_evaluations, get_evaluation_details, delete_evaluation, create_testset_using_ragas
from utils.rag_evaluator import get_queries_response, fetch_testset_files
import requests


TESTSET_DIR = Path(__file__).parent.parent / "data" / "testset_generation"

def show_evaluation_page():
    """Display the RAG evaluation page"""
    st.title("RAG Evaluation Dashboard")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Run Evaluation", "View Results", "Create Testset"])
    
    with tab1:
        show_run_evaluation_tab()
    
    with tab2:
        show_results_tab()

    with tab3:
        show_create_testset_tab()

def show_run_evaluation_tab():
    """Display the tab for running evaluations"""
    st.header("Run New Evaluation")

    # Query method selection
    query_method = st.radio("Query Input Method", ["Send a Query", "Upload File"], horizontal=True)

    if query_method == "Send a Query":
        st.subheader("Send a Query")
        
        queries = st.text_area(
            "Enter queries (one per line)",
            "What is RAG?\nHow does vector search work?\nExplain embedding models."
        )

        if st.button("Run Query"):
            if not queries.strip():
                st.error("Please enter at least one query.")
                return

            with st.spinner("Fetching responses..."):
                query_list = [q.strip() for q in queries.split("\n") if q.strip()]
                results = get_queries_response(query_list)

            st.subheader("Query Results")
            for res in results:
                with st.expander(f"Query: {res['question']}"):
                    st.write("**Answer**")
                    st.write(res.get("answer", "No answer available"))

                    st.write("**Sources**")
                    st.write(res.get("sources", "No sources found"))

    elif query_method == "Upload File":
        st.subheader("Upload Query File")
        
        with st.form("evaluation_form"):
            eval_name = st.text_input("Evaluation Name", f"Evaluation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}")
            eval_description = st.text_area("Description", "RAG system evaluation")

            query_file = st.file_uploader("Upload query file (CSV or TXT)", type=["csv", "txt"])

            st.subheader("Evaluation Parameters")
            col1, col2 = st.columns(2)
            with col1:
                relevance_threshold = st.slider("Relevance Threshold", 0.0, 1.0, 0.7)
                top_k = st.slider("Top K Results", 1, 20, 5)
            with col2:
                metrics = st.multiselect(
                    "Metrics to Calculate",
                    ["Precision", "Recall", "F1", "MRR", "NDCG", "Latency"],
                    default=["Precision", "Recall", "F1", "MRR"]
                )

            submit = st.form_submit_button("Run Evaluation")

        if submit:
            if query_file is None:
                st.error("Please upload a query file.")
                return

            with st.spinner("Running evaluation..."):
                # Process file
                if query_file.type == "text/csv":
                    df = pd.read_csv(query_file)
                    query_set = df.iloc[:, 0].tolist()  # Assume first column contains queries
                else:
                    content = query_file.getvalue().decode()
                    query_set = [line.strip() for line in content.split("\n") if line.strip()]

                parameters = {
                    "name": eval_name,
                    "description": eval_description,
                    "relevance_threshold": relevance_threshold,
                    "top_k": top_k,
                    "metrics": metrics
                }

                eval_id, results = run_evaluation(query_set, parameters)

                st.success(f"Evaluation completed! ID: {eval_id}")

                st.subheader("Summary Results")
                metric_cols = st.columns(4)
                metrics_to_show = {
                    "Precision": results.get("precision", 0),
                    "Recall": results.get("recall", 0),
                    "F1 Score": results.get("f1_score", 0),
                    "MRR": results.get("mrr", 0)
                }

                for i, (metric, value) in enumerate(metrics_to_show.items()):
                    with metric_cols[i % 4]:
                        st.metric(label=metric, value=f"{value:.2f}")

                if st.button("View Detailed Results"):
                    st.session_state.selected_eval_id = eval_id
                    st.session_state.selected_eval_results = results
                    st.rerun()

def show_results_tab():
    """Display the tab for viewing evaluation results"""
    st.header("Evaluation Results")
    
    # Get list of evaluations
    evaluations = list_evaluations()
    
    if not evaluations:
        st.info("No evaluations have been run yet.")
        return
    
    # Convert to DataFrame for display
    eval_data = []
    for eval_id, eval_info in evaluations.items():
        eval_data.append({
            "ID": eval_id,
            "Name": eval_info["name"],
            "Date": eval_info["timestamp"],
            "Queries": eval_info.get("num_queries", 0),
            "Precision": eval_info.get("metrics", {}).get("precision", 0),
            "Recall": eval_info.get("metrics", {}).get("recall", 0),
            "F1": eval_info.get("metrics", {}).get("f1_score", 0),
            "MRR": eval_info.get("metrics", {}).get("mrr", 0)
        })
    
    eval_df = pd.DataFrame(eval_data)
    
    # Sort by date (newest first)
    eval_df = eval_df.sort_values("Date", ascending=False).reset_index(drop=True)
    
    # Display the dataframe
    st.dataframe(eval_df)
    
    # Select evaluation to view
    st.subheader("View Evaluation Details")
    
    eval_ids = eval_df["ID"].tolist()
    eval_names = eval_df["Name"].tolist()
    
    if not eval_ids:
        return
    
    # Use session state for selection if available
    default_index = 0
    if hasattr(st.session_state, "selected_eval_id") and st.session_state.selected_eval_id in eval_ids:
        default_index = eval_ids.index(st.session_state.selected_eval_id)
        # Clear it after use
        del st.session_state.selected_eval_id
    
    selected_index = st.selectbox(
        "Select an evaluation to view:",
        range(len(eval_ids)),
        format_func=lambda i: f"{eval_names[i]} ({eval_ids[i]})",
        index=default_index
    )
    
    selected_eval_id = eval_ids[selected_index]
    
    # Get detailed evaluation data
    eval_details = get_evaluation_details(selected_eval_id)
    
    if eval_details:
        # Display evaluation details
        st.subheader(eval_details.get("name", "Evaluation Details"))
        st.write(f"**Description**: {eval_details.get('description', 'N/A')}")
        st.write(f"**Date**: {eval_details.get('timestamp', 'N/A')}")
        
        # Display metrics
        metric_cols = st.columns(4)
        metrics = {
            "Precision": eval_details.get("precision", 0),
            "Recall": eval_details.get("recall", 0),
            "F1 Score": eval_details.get("f1_score", 0),
            "MRR": eval_details.get("mrr", 0)
        }
        
        for i, (metric, value) in enumerate(metrics.items()):
            with metric_cols[i % 4]:
                st.metric(label=metric, value=f"{value:.2f}")
        
        # Display visualization
        st.subheader("Metrics Visualization")
        
        # Bar chart of metrics
        fig, ax = plt.subplots(figsize=(10, 5))
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        # Create bars with different colors
        bars = ax.bar(
            metric_names, 
            metric_values,
            color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        )
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.02,
                f'{height:.2f}',
                ha='center', 
                va='bottom'
            )
        
        ax.set_ylim(0, 1.1)  # Set y-axis from 0 to 1.1 to have space for labels
        ax.set_title('Evaluation Metrics')
        ax.set_ylabel('Score')
        
        # Display the chart
        st.pyplot(fig)
        
        # Display individual query results
        st.subheader("Query Results")
        queries = eval_details.get("queries", [])
        
        if queries:
            query_df = pd.DataFrame(queries)
            st.dataframe(query_df)
        else:
            st.info("No detailed query results available.")
        
        # Delete button
        if st.button("Delete Evaluation"):
            success, message = delete_evaluation(selected_eval_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.error("Could not load evaluation details.")

def show_testset_history():
    DOWNLOAD_URL = "http://localhost:8000/download?file="

    """Display testset file history in Streamlit with download buttons"""
    response = fetch_testset_files()

    if not response["success"]:
        st.warning(response["message"])
        return

    file_data = response["files"]

    st.subheader("Testset Files History")

    for file in file_data:
        filename = file["filename"]
        dt_str = file["datetime"]

        col1, col2, col3 = st.columns([4, 2, 1])
        col1.text(filename)
        col2.text(dt_str)

        # Create a direct download link instead of a new button
        col3.markdown(
            f'<a href="{DOWNLOAD_URL}{filename}" download="{filename}" target="_blank">'
            f'<button style="padding: 5px 10px; background-color: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer;">Download</button>'
            f'</a>',
            unsafe_allow_html=True
        )
def show_create_testset_tab():
    st.header("Testset Generation")

    with st.form(key="create testset"):
        num_of_test = st.number_input(
            "Enter desired number of testset data",
            min_value=1,  # Minimum value allowed
            step=1,        # Increment step
            format="%d"    # Display as an integer
        )
        submit_button = st.form_submit_button(label="Create Now")

    if submit_button:
        response = create_testset_using_ragas(num_of_test=num_of_test)

        if response["status"]:  # Check if the request was successful
            st.success(response["message"])

            # Extract only the generated testset and convert it into a DataFrame
            testset_data = response["data"]  # Extract JSON data
            testset_df = pd.DataFrame(testset_data)  # Convert JSON to DataFrame

            # Display the DataFrame in Streamlit
            st.dataframe(testset_df)
        else:
            st.error(response["message"])

    show_testset_history()
    