from app.services.storage.minio import MinioStorage
from app.config import settings

def get_storage():
    if settings.STORAGE_PROVIDER == "minio":
        return MinioStorage()