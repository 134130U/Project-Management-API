import requests
from frontend.services.api import get_api_url

class ProjectService:
    @staticmethod
    def get_projects(token):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(get_api_url("/projects"), headers=headers)
        return response

    @staticmethod
    def create_project(token, name, status, description, priority=None, start_date=None, end_date=None, budget=0, spent=0, team=None, stakeholders=None, tags=None, file_content=None, filename=None, content_type=None):
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": name,
            "status": status,
            "description": description,
            "priority": priority,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "spent": spent,
            "team": team,
            "stakeholders": stakeholders,
            "tags": tags
        }
        
        if file_content:
            files = {
                "file": (filename, file_content, content_type)
            }
            response = requests.post(get_api_url("/projects"), headers=headers, data=data, files=files)
        else:
            response = requests.post(get_api_url("/projects"), headers=headers, data=data)
            
        return response

    @staticmethod
    def update_project(token, project_id, data):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(get_api_url(f"/projects/{project_id}"), headers=headers, json=data)
        return response

    @staticmethod
    def get_updates(token, project_id):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(get_api_url(f"/updates/{project_id}"), headers=headers)
        return response

    @staticmethod
    def create_update(token, project_id, title, description):
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "project_id": project_id,
            "title": title,
            "description": description
        }
        response = requests.post(get_api_url("/updates"), headers=headers, json=data)
        return response

    @staticmethod
    def upload_file(token, update_id, file_content, filename, content_type):
        headers = {"Authorization": f"Bearer {token}"}
        files = {
            "file": (filename, file_content, content_type)
        }
        response = requests.post(get_api_url(f"/files/upload/{update_id}"), headers=headers, files=files)
        return response

    @staticmethod
    def get_file_download_url(token, file_id):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(get_api_url(f"/files/download/{file_id}"), headers=headers)
        return response
