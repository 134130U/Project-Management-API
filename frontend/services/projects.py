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
