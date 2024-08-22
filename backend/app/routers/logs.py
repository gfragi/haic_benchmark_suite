import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from jsonschema import ValidationError
from sqlalchemy.orm import Session
from app.models import LogEntry, EvaluationConfig
from app.schemas.log import LogSchema
from app.utils.database import get_db
from app.utils.generic_functions import get_config_by_id, save_log_entry
from app.schemas.evaluation_config import EnergyConfigSchema, GenericConfigSchema, RadiologyConfigSchema, SmartCitiesConfigSchema

router = APIRouter()

# @router.post("/", response_model=LogSchema)
# def create_log(log: LogSchema, db: Session = Depends(get_db)):
#     config = db.query(EvaluationConfig).filter(EvaluationConfig.id == log.evaluation_config_id).first()
#     if not config:
#         raise HTTPException(status_code=404, detail="Evaluation configuration not found")

#     log_entry = LogEntry(
#         session_id=log.session_id,
#         user_id=log.user_id,
#         ai_model_version=log.ai_model_version,
#         app_version=log.app_version,
#         start_time=log.start_time,
#         end_time=log.end_time,
#         interaction_data=log.interaction_data,
#         retrain_events=log.retrain_events,
#         evaluation_config_id=log.evaluation_config_id
#     )

#     db.add(log_entry)
#     db.commit()
#     db.refresh(log_entry)
#     return log_entry

@router.post("/upload-log")
async def upload_log(config_id: int, file: UploadFile = File(...)):
    config = await get_config_by_id(config_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")
    
    content = await file.read()
    try:
        json_data = json.loads(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    
    # Determine which schema to use based on the config type
    if config.config_type == 'specific':
        if config.application_name == 'RadiologyApp':
            schema = RadiologyConfigSchema
        elif config.application_name == 'SmartCities':
            schema = SmartCitiesConfigSchema
        elif config.application_name == 'Energy':
            schema = EnergyConfigSchema
        else:
            raise HTTPException(status_code=400, detail="Unknown application type.")
    else:
        schema = GenericConfigSchema
    
    try:
        validated_log = schema(**json_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Log file structure invalid: {e}")
    
    # Save the validated log to the database
    log_entry = LogEntry(**validated_log.dict())
    log_entry.evaluation_config_id = config_id
    await save_log_entry(log_entry)
    
    return {"detail": "Log file successfully uploaded and associated with evaluation configuration."}



@router.post("/{log_id}/associate-config/")
async def associate_log_with_config(log_id: int, config_id: int, db: Session = Depends(get_db)):
    log_entry = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found.")

    evaluation_config = db.query(EvaluationConfig).filter(EvaluationConfig.id == config_id).first()
    if not evaluation_config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    # Assuming a relationship between LogEntry and EvaluationConfig exists
    log_entry.evaluation_config_id = evaluation_config.id
    db.commit()
    return {"message": "Log successfully associated with the evaluation configuration."}