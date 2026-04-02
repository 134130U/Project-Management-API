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
    def upload(self, file_data):
        import io
        if isinstance(file_data, bytes):
            file_obj = io.BytesIO(file_data)
            length = len(file_data)
        else:
            file_obj = file_data
            # Try to get length if it's a file-like object
            try:
                file_obj.seek(0, 2)
                length = file_obj.tell()
                file_obj.seek(0)
            except:
                length = -1

        key = str(uuid.uuid4())
        self.client.put_object(
            settings.MINIO_BUCKET,
            key,
            file_obj,
            length=length,
            part_size=10*1024*1024 if length == -1 or length > 10*1024*1024 else 5*1024*1024
        )
        return key

    def get_url(self, key):
        return self.client.presigned_get_object(settings.MINIO_BUCKET, key)

    def delete(self, key):
        self.client.remove_object(settings.MINIO_BUCKET, key)