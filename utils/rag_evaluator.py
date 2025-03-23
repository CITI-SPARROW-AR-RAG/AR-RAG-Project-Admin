import json
import os
import datetime
from pathlib import Path
import pandas as pd
from datetime import datetime

# Define constants
EVALUATIONS_DIR = Path(__file__).parent.parent / "data" / "evaluations"
EVAL_INDEX = Path(__file__).parent.parent / "data" / "evaluation_index.json"
TESTSET_DIR = Path(__file__).parent.parent / "data" / "testset_generation"

# Ensure directories exist
os.makedirs(EVALUATIONS_DIR, exist_ok=True)

def save_evaluation_result(evaluation_data):
    """Save a RAG evaluation result"""
    if not os.path.exists(EVAL_INDEX):
        with open(EVAL_INDEX, 'w') as f:
            json.dump({}, f)
    
    # Generate evaluation ID using timestamp
    eval_id = f"eval_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Add metadata
    evaluation_data["timestamp"] = str(datetime.datetime.now())
    
    # Save evaluation data
    eval_file = os.path.join(EVALUATIONS_DIR, f"{eval_id}.json")
    with open(eval_file, 'w') as f:
        json.dump(evaluation_data, f, indent=4)
    
    # Update index
    with open(EVAL_INDEX, 'r') as f:
        eval_index = json.load(f)
    
    eval_index[eval_id] = {
        "name": evaluation_data.get("name", eval_id),
        "timestamp": evaluation_data["timestamp"],
        "metrics": {
            k: v for k, v in evaluation_data.items() 
            if k in ["precision", "recall", "f1_score", "accuracy", "mrr", "ndcg"]
        },
        "num_queries": len(evaluation_data.get("queries", [])),
        "file_path": eval_file
    }
    
    with open(EVAL_INDEX, 'w') as f:
        json.dump(eval_index, f, indent=4)
    
    return eval_id

def list_evaluations():
    """Get a list of all evaluations with their metadata"""
    if not os.path.exists(EVAL_INDEX):
        return {}
    
    with open(EVAL_INDEX, 'r') as f:
        eval_index = json.load(f)
    
    return eval_index

def get_evaluation_details(eval_id):
    """Get full details for a specific evaluation"""
    if not os.path.exists(EVAL_INDEX):
        return None
    
    with open(EVAL_INDEX, 'r') as f:
        eval_index = json.load(f)
    
    if eval_id not in eval_index:
        return None
    
    eval_file = eval_index[eval_id]["file_path"]
    if not os.path.exists(eval_file):
        return None
    
    with open(eval_file, 'r') as f:
        eval_data = json.load(f)
    
    return eval_data

def delete_evaluation(eval_id):
    """Delete an evaluation and its data"""
    if not os.path.exists(EVAL_INDEX):
        return False, "Evaluation index not found"
    
    with open(EVAL_INDEX, 'r') as f:
        eval_index = json.load(f)
    
    if eval_id not in eval_index:
        return False, "Evaluation not found"
    
    # Get the file info
    eval_file = eval_index[eval_id]["file_path"]
    
    # Delete the file if it exists
    if os.path.exists(eval_file):
        os.remove(eval_file)
    
    # Remove from index
    del eval_index[eval_id]
    
    # Update index file
    with open(EVAL_INDEX, 'w') as f:
        json.dump(eval_index, f, indent=4)
    
    return True, "Evaluation deleted successfully"

# Example function for running an evaluation - replace with your actual implementation
def run_evaluation(query_set, parameters):
    """Run a RAG evaluation on a set of queries"""
    # This is a placeholder - replace with your actual evaluation logic
    
    # Example result structure
    results = {
        "name": parameters.get("name", "Evaluation"),
        "description": parameters.get("description", ""),
        "parameters": parameters,
        "precision": 0.85,
        "recall": 0.78,
        "f1_score": 0.81,
        "mrr": 0.92,
        "ndcg": 0.88,
        "queries": [
            {
                "query": q,
                "expected": "Expected result",
                "actual": "Actual result",
                "score": 0.9,
                "latency_ms": 150
            }
            for q in query_set
        ]
    }
    
    # Save results
    eval_id = save_evaluation_result(results)
    
    return eval_id, results

def create_testset_using_ragas(num_of_test):
    dummy_data = {
        'index': [i for i in range(0,10)],
        'question': [i for i in range(0,10)],
        'reference': [i for i in range(0,10)],
        'retrieved_context': [i for i in range(0,10)],
    }
    testset_df = pd.DataFrame(dummy_data)

    file_name = datetime.now().strftime("testset_%Y%m%d_%H%M%S.csv")
    testset_df.to_csv(os.path.join(TESTSET_DIR, file_name), index=False)

    return True, "Testset data created successfully", testset_df

