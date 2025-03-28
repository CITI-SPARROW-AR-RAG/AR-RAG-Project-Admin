import requests

API_URL = "http://localhost:8080/admin/get_queries_response"
payload = ["what is 1+1", "what is 1+2"]

try:
    response = requests.post(API_URL, json=payload)
    print(response.json())
except Exception as e:
    print(f"Error: {e}")