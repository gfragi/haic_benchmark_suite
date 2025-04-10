import json
import logging
import os
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from jsonschema import ValidationError
from minio import Minio, S3Error
from sqlalchemy.orm import Session
from app.models import LogEntry
from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.generic_functions import save_log_entry, get_config_by_id
from app.utils.minio_utils import upload_file
from app.models.configuration import EvaluationConfig
from app.utils.minio_client_keycloak import get_minio_client

router = APIRouter()

# Initialize a logger
logger = logging.getLogger(__name__)

load_dotenv()

minio_client = get_minio_client()


@router.post("/upload")
async def upload_log(configuration_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Fetch the configuration to associate with the logs
    config = get_config_by_id(configuration_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    # Read the content of the file
    content = await file.read()

    # Attempt to parse the JSON content
    try:
        json_data = json.loads(content.decode('utf-8'))  # Ensure decoding of bytes to string
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e.msg}")

    # Process each log in the JSON array
    if not isinstance(json_data, list):
        raise HTTPException(status_code=400, detail="Expected a list of logs")

    # Validate each log against the schema
    for log_data in json_data:
        try:
            validated_log = LogSchema(**log_data)
            log_entry_data = jsonable_encoder(validated_log)
            log_entry_data['configuration_id'] = configuration_id
            log_entry = LogEntry(**log_entry_data)
            # db.add(log_entry)
        except ValidationError as e:
            # Log the error if validation fails and skip this log
            logger.error(f"Log file structure invalid: {e}")
            continue

    # Commit valid logs to the database
    db.commit()

    # Upload the original file to MinIO (not the parsed JSON)
    try:
        minio_path = await upload_file(content, configuration_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload log file to MinIO: {str(e)}")

    # Store the MinIO path in the database
    config.minio_path = minio_path
    db.commit()

    return {"detail": f"Successfully uploaded the log file and associated it with configuration ID {configuration_id}.", "minio_path": minio_path}



@router.get("/{config_id}")
def list_logs(config_id: int):
    # List objects in the config's folder
    try:
        objects = minio_client.list_objects(os.getenv("MINIO_BUCKET"), prefix=f"{config_id}/", recursive=True)
        log_files = [obj.object_name for obj in objects]
        return {"logs": log_files}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{config_id}/{log_name}")
def download_log(config_id: int, log_name: str):
    try:
        log_path = f"{config_id}/{log_name}"
        url = minio_client.presigned_get_object(os.getenv("MINIO_BUCKET"), log_path)
        return {"download_url": url}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_id}/{log_name}")
def delete_log(config_id: int, log_name: str):
    try:
        log_path = f"{config_id}/{log_name}"
        minio_client.remove_object(os.getenv("MINIO_BUCKET"), log_path)
        return {"detail": "Log deleted successfully"}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))


# Log registration in database
@router.post("/register")
def register_log(log: LogSchema, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == log.config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    new_log = Log(name=log.name, config_id=log.config_id, minio_path=log.minio_path)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log