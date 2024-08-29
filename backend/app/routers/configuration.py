from datetime import datetime as dt
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.configuration import EvaluationConfig
from app.schemas.configuration import EvaluationConfigSchema
from app.services.metrics import Metrics

router = APIRouter()

logger = logging.getLogger(__name__)

# POST endpoint to create a new evaluation configuration
@router.post("/new", response_model=EvaluationConfigSchema)
def create_configuration(config: EvaluationConfigSchema, db: Session = Depends(get_db)):
    # Retrieve the selected groups
    selected_groups = config.metrics
    
    # Expand the groups into individual metrics
    available_metrics = Metrics.get_available_metrics()
    selected_metrics = []

    for group in selected_groups:
        if group in available_metrics:
            selected_metrics.extend(available_metrics[group])
        else:
            raise HTTPException(status_code=400, detail=f"Group {group} not found in available metrics.")
    
    # Remove duplicates if any (optional, depends on your needs)
    selected_metrics = list(set(selected_metrics))

    new_config = EvaluationConfig(
        application_name=config.application_name,
        ai_model_name=config.ai_model_name,
        ai_model_type=config.ai_model_type,
        description=config.description,
        metrics=selected_metrics,  # Save the expanded list of metrics
        evaluation_date=dt.utcnow(),
        config_type=config.config_type,
        evaluation_status=config.evaluation_status
    )
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config


# GET endpoint to retrieve an evaluation configuration by ID
@router.get("/{configuration_id}", response_model=EvaluationConfigSchema)
def get_configuration(configuration_id: int, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")
    return config


# GET endpoint to list all evaluation configurations
@router.get("/list/", response_model=List[EvaluationConfigSchema])
def get_all_configurations(db: Session = Depends(get_db)):
    return db.query(EvaluationConfig).all()



# PUT endpoint to update an evaluation configuration
@router.put("/update/{configuration_id}", response_model=EvaluationConfigSchema)
def update_configuration(configuration_id: int, updated_config: EvaluationConfigSchema, db: Session = Depends(get_db)):
    # Retrieve the existing config
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")

    # Update the config fields
    config.application_name = updated_config.application_name
    config.ai_model_name = updated_config.ai_model_name
    config.description = updated_config.description
    config.evaluation_date = updated_config.evaluation_date
    config.config_type = updated_config.config_type
    config.metrics = updated_config.metrics

    # Commit the changes to the database
    db.commit()
    db.refresh(config)

    return config

# DELETE endpoint to delete an evaluation configuration
@router.delete("/delete/{configuration_id}", response_model=dict)
def delete_configuration(configuration_id: int, db: Session = Depends(get_db)):
    # Retrieve the existing config
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")

    # Delete the config
    db.delete(config)
    db.commit()

    return {"message": f"Evaluation configuration with id {configuration_id} has been deleted."}
