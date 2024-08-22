import json
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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
    config = get_config_by_id(configuration_id, db)

    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    content = await file.read()
    try:
        json_data = json.loads(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")

    try:
        # Validate against LogSchema
        validated_log = LogSchema(**json_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Log file structure invalid: {e}")

    # Manually extract the relevant fields to populate LogEntry
    log_entry_data = validated_log.dict(exclude_unset=True)

    # Associate with the configuration ID
    log_entry_data["configuration_id"] = configuration_id

    # Save the validated log to the database
    log_entry = LogEntry(**log_entry_data)
    save_log_entry(log_entry, db)

    return {"detail": "Log file successfully uploaded and associated with evaluation configuration."}


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