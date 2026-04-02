import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def get_api_url(endpoint):
    return f"{API_BASE_URL}/{endpoint.lstrip('/')}"

class APIService:
    @staticmethod
    def get(endpoint, token=None, params=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(get_api_url(endpoint), headers=headers, params=params)
        return response

    @staticmethod
    def post(endpoint, token=None, json=None, data=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.post(get_api_url(endpoint), headers=headers, json=json, data=data)
        return response

    @staticmethod
    def put(endpoint, token=None, json=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.put(get_api_url(endpoint), headers=headers, json=json)
        return response

    @staticmethod
    def delete(endpoint, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.delete(get_api_url(endpoint), headers=headers)
        return response
