from fastapi import FastAPI, APIRouter
from app.api.routes import auth, projects, updates, files

app = FastAPI(title="Project Management API")
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(updates.router)
api_router.include_router(files.router)

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}