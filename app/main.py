from fastapi import FastAPI
from app.api.routes import auth, projects, updates, files

app = FastAPI(title="Project Management API")

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(updates.router)
app.include_router(files.router)

@app.get("/health")
def health():
    return {"status": "ok"}