from minio import Minio
from app.config import settings
import uuid

class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
    def upload(self, file):
        key = str(uuid.uuid4())
        self.client.put_object(
            settings.MINIO_BUCKET,
            key,
            file,
            length=-1,
            part_size=10*1024*1024
        )
        return key

    def get_url(self, key):
        return self.client.presigned_get_object(settings.MINIO_BUCKET, key)