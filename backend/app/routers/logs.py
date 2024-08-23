import json
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from jsonschema import ValidationError
from sqlalchemy.orm import Session
from app.models import LogEntry, EvaluationConfig
from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.generic_functions import save_log_entry, get_config_by_id


router = APIRouter()

# Initialize a logger
logger = logging.getLogger(__name__)

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
    except JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e.msg}")

    # Process each log in the JSON array
    if not isinstance(json_data, list):
        raise HTTPException(status_code=400, detail="Expected a list of logs")

    # Validate and save each log
    for log_data in json_data:
        try:
            validated_log = LogSchema(**log_data)
            log_entry_data = jsonable_encoder(validated_log)
            log_entry_data['configuration_id'] = configuration_id
            log_entry = LogEntry(**log_entry_data)
            db.add(log_entry)
        except ValidationError as e:
            # If validation fails, you can either stop processing or log the error and continue
            continue

    db.commit()
    return {"detail": f"Successfully uploaded {len(json_data)} logs and associated them with configuration ID {configuration_id}."}


@router.get("/list/")
async def list_logs(db: Session = Depends(get_db)):
    logs = db.query(LogEntry).all()
    return logs


@router.delete("/delete/{log_id}")
async def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found.")
    db.delete(log)
    db.commit()
    return {"detail": "Log entry deleted."}

@router.put("/update/{log_id}")
async def update_log(log_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Fetch the existing log entry by log_id
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found.")

    # Read the content of the uploaded file
    content = await file.read()

    try:
        # Parse the JSON data from the uploaded file
        json_data = json.loads(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")

    # Validate the JSON data against the LogSchema
    try:
        validated_log = LogSchema(**json_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Log file structure invalid: {e}")

    # Update the existing log entry with the validated data
    log.session_id = validated_log.session_id
    log.user_id = validated_log.user_id
    log.ai_model_version = validated_log.ai_model_version
    log.app_version = validated_log.app_version
    log.start_time = validated_log.start_time
    log.end_time = validated_log.end_time
    log.interaction_data = validated_log.interaction_data.dict()  # Convert to dictionary
    log.retrain_events = [event.dict() for event in validated_log.retrain_events]  # Convert list of objects to list of dictionaries
    log.performance_infrastructure = validated_log.performance_infrastructure.dict()  # Convert to dictionary
    log.performance_logs = validated_log.performance_logs.dict()  # Convert to dictionary
    log.ai_model_data = validated_log.ai_model_data.dict()  # Convert to dictionary

    # Commit the changes to the database
    db.commit()
    
    return {"detail": "Log entry updated successfully."}