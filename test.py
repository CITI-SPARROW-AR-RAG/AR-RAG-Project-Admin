import requests

API_URL = "http://127.0.0.1:8000/admin/get_users"
response = requests.get(API_URL)

if response.status_code == 200:
    print("Users:", response.json())
else:
    print("Error:", response.status_code, response.text)
