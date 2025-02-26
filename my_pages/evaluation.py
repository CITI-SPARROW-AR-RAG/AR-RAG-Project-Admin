import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.rag_evaluator import run_evaluation, list_evaluations, get_evaluation_details, delete_evaluation

def show_evaluation_page():
    """Display the RAG evaluation page"""
    st.title("RAG Evaluation Dashboard")
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["Run Evaluation", "View Results"])
    
    with tab1:
        show_run_evaluation_tab()
    
    with tab2:
        show_results_tab()

def show_run_evaluation_tab():
    """Display the tab for running evaluations"""
    st.header("Run New Evaluation")
    
    with st.form("evaluation_form"):
        # Basic info
        eval_name = st.text_input("Evaluation Name", f"Evaluation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}")
        eval_description = st.text_area("Description", "RAG system evaluation")
        
        # Query set
        st.subheader("Query Set")
        query_method = st.radio("Query Input Method", ["Text Input", "Upload File"], horizontal=True)
        
        queries = None  # Initialize queries variable to handle both cases
        
        if query_method == "Text Input":
            queries = st.text_area(
                "Enter queries (one per line)",
                "What is RAG?\nHow does vector search work?\nExplain embedding models."
            )
        elif query_method == "Upload File":
            query_file = st.file_uploader("Upload query file (CSV or TXT)", type=["csv", "txt"])
        
        # Evaluation parameters
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
        
        # Submit button
        submit = st.form_submit_button("Run Evaluation")
        
        if submit:
            # If Text Input is used, ensure queries are provided
            if query_method == "Text Input" and queries:
                st.success(f"Running evaluation with the following queries:\n{queries}")
            elif query_method == "Upload File" and query_file:
                st.success(f"Running evaluation with queries from file: {query_file.name}")
            else:
                st.error("Please provide valid input for queries (either text or file).")


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