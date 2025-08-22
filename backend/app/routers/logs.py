import json
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from jsonschema import ValidationError
from sqlalchemy.orm import Session

from app.models import LogEntry
from app.models.configuration import EvaluationConfig
from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.generic_functions import get_config_by_id
from app.utils.minio_utils import upload_file, list_files, download_file, delete_file

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

router = APIRouter()
logger = logging.getLogger(__name__)

load_dotenv()


@router.post("/upload")
async def upload_log(configuration_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Fetch config to associate logs
    config = get_config_by_id(configuration_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    # Read file
    content = await file.read()

    # Validate JSON
    try:
        json_data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e.msg}")

    if not isinstance(json_data, list):
        raise HTTPException(status_code=400, detail="Expected a list of logs")

    # Validate logs
    for log_data in json_data:
        try:
            validated_log = LogSchema(**log_data)
            log_entry_data = jsonable_encoder(validated_log)
            log_entry_data["configuration_id"] = configuration_id
            log_entry = LogEntry(**log_entry_data)
            # db.add(log_entry)  # uncomment to persist
        except ValidationError as e:
            logger.error(f"Log structure invalid: {e}")
            continue

    db.commit()

    # Upload original file to MinIO
    try:
        minio_path = await upload_file(content, configuration_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload log file to MinIO: {str(e)}")

    config.minio_path = minio_path
    db.commit()

    return {"detail": f"Successfully uploaded log for config {configuration_id}.", "minio_path": minio_path}


@router.get("/{config_id}")
def get_logs(config_id: int):
    try:
        return {"logs": list_files(config_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{config_id}/{log_name}")
def get_download_url(config_id: int, log_name: str):
    try:
        return {"download_url": download_file(config_id, log_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_id}/{log_name}")
def remove_log(config_id: int, log_name: str):
    try:
        delete_file(config_id, log_name)
        return {"detail": "Log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
def register_log(log: LogSchema, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == log.config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    new_log = LogEntry(name=log.name, config_id=log.config_id, minio_path=log.minio_path)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
