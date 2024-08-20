from fastapi import UploadFile
from minio import Minio
import uuid
import io

import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
 # MinIO setup


client = Minio(
        os.getenv("MINIO_ENDPOINT"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False,
        region=os.getenv("MINIO_REGION"),
)


async def upload_model(upload_file: UploadFile, task_id: int) -> str:
    # Generate a unique filename with task_id prefix
    filename = f"task_{task_id}_{uuid.uuid4()}.json"
    object_name = os.path.join(str(task_id), filename)

    # Upload the model file
    data = await upload_file.read()  # Read the file data

    client.put_object(
        os.getenv("MINIO_BUCKET"), object_name, io.BytesIO(data), len(data),
    )

    model_path = object_name # Return the path to the model file in MinIO
    return model_path


async def upload_dataset(dataset_file: UploadFile, task_id: int) -> str:

    # Generate a unique filename with task_id prefix
    filename = f"task_{task_id}_{uuid.uuid4()}.csv"
    object_name = os.path.join(str(task_id), filename)

    # Upload the dataset file
    data = await dataset_file.read()  # Read the file data
    client.put_object(
        os.getenv("MINIO_BUCKET"), object_name, io.BytesIO(data), len(data),
    )
    dataset_path = object_name  # Return the path to the dataset file in MinIO
    return dataset_path