from fastapi import UploadFile
from minio import Minio

# from logging import getLogger
import uuid
import io

import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
# MinIO setup

# logger = getLogger(__name__)

print(
    "Loading MinIO configuration from environment variables:",
    os.getenv("MINIO_ENDPOINT"),
    os.getenv("MINIO_ACCESS_KEY"),
    os.getenv("MINIO_SECRET_KEY"),
    os.getenv("MINIO_REGION"),
)


client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=True,
    region=os.getenv("MINIO_REGION"),
)


async def upload_file(file_data: bytes, config_id: int) -> str:
    # Generate a unique filename with config_id prefix
    # filename = f"config_{config_id}_{uuid.uuid4()}.json"
    filename = f"config_{config_id}.json"
    object_name = os.path.join(str(config_id), filename)

    # Upload the file data
    client.put_object(
        os.getenv("MINIO_BUCKET"), object_name, io.BytesIO(file_data), len(file_data)
    )

    file_path = object_name  # Return the path to the file in MinIO
    return file_path
