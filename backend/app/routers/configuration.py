from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.configuration import EvaluationConfig, Metric
from app.schemas.log import LogSchema  # Using LogSchema for validation
from pydantic import BaseModel  # Importing BaseModel if needed

router = APIRouter()

# POST endpoint to create a new evaluation configuration
@router.post("/new", response_model=LogSchema)
def create_configuration(config: LogSchema, db: Session = Depends(get_db)):
    db_metrics = []
    for metric in config.metrics:
        db_metric = db.query(Metric).filter(Metric.metric_name == metric.metric_name).first()
        if not db_metric:
            db_metric = Metric(**metric.dict())
            db.add(db_metric)
            db.commit()
            db.refresh(db_metric)
        db_metrics.append(db_metric)

    db_config = EvaluationConfig(
        application_name=config.interaction_data.application_id,
        config_type=config.config_type,
        ai_model_name=config.ai_model_data.ai_model_name,
        description=config.description,
        metrics=db_metrics,
        evaluation_date=config.evaluation_date
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

# GET endpoint to retrieve an evaluation configuration by ID
@router.get("/{configuration_id}", response_model=LogSchema)
def get_configuration(configuration_id: int, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")
    return config

# GET endpoint to list all evaluation configurations
@router.get("/list", response_model=List[LogSchema])
def get_all_configurations(db: Session = Depends(get_db)):
    return db.query(EvaluationConfig).all()

# PUT endpoint to update an evaluation configuration
@router.put("/update/{configuration_id}", response_model=LogSchema)
def update_configuration(configuration_id: int, updated_config: LogSchema, db: Session = Depends(get_db)):
    # Retrieve the existing config
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")

    # Update the config fields
    config.application_name = updated_config.interaction_data.application_id
    config.ai_model_name = updated_config.ai_model_data.ai_model_name
    config.description = updated_config.description
    config.evaluation_date = updated_config.evaluation_date
    config.config_type = updated_config.config_type

    # Handle metrics update
    if updated_config.metrics:
        # Clear existing metrics relationships
        config.metrics.clear()

        # Add updated metrics
        for metric in updated_config.metrics:
            db_metric = db.query(Metric).filter(Metric.metric_name == metric.metric_name).first()
            if not db_metric:
                db_metric = Metric(**metric.dict())
                db.add(db_metric)
                db.commit()
                db.refresh(db_metric)
            config.metrics.append(db_metric)

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
