import os
import sys
from minio import Minio
from minio.error import S3Error

# Add project root to path to import settings
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

def main():
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )

    bucket_name = settings.MINIO_BUCKET

    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
