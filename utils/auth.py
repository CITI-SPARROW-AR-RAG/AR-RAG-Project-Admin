import streamlit as st
import json
import os
import hashlib
import secrets
import string
from pathlib import Path
import requests

def check_login(username, password):
    API_URL = "http://127.0.0.1:8000/admin/check_login"
    response = requests.get(API_URL, params={"username": username, "password": password})
    return response

def create_user(username, password, created_by):
    API_URL = "http://127.0.0.1:8000/admin/create_user"
    response = requests.get(API_URL, params={"username": username, "password": password, "created_by": created_by})
    
    data = response.json()
    return data["success"], data["message"]