from .api import APIService

class AuthService:
    @staticmethod
    def login(email, password):
        return APIService.post("/auth/login", json={"email": email, "password": password})

    @staticmethod
    def register(email, password):
        return APIService.post("/auth/register", json={"email": email, "password": password})
