import datetime
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.metrics import Metrics
from app.utils.generic_functions import get_config_by_id
from fastapi import BackgroundTasks

from app.models.configuration import EvaluationConfig
from app.services.evaluate import run_evaluation
from app.utils.generic_functions import get_config_by_id
from app.models.results import Metric, MetricGroup, MetricGroupResponse


router = APIRouter()

# Trigger Evaluation Endpoint
@router.post("/{configuration_id}")
async def evaluate_config(configuration_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Fetch the configuration by ID
    config = get_config_by_id(configuration_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Update the status to running
    config.evaluation_status = EvaluationConfig.STATUS_RUNNING
    db.commit()

    # Run the evaluation in the background, passing the config ID
    background_tasks.add_task(run_evaluation, configuration_id)

    return {"detail": "Evaluation started successfully"}

# Endpoint to fetch all metrics, grouped by MetricGroup name, with group descriptions
@router.get("/metrics", response_model=Dict[str, MetricGroupResponse])
def get_metrics(db: Session = Depends(get_db)):
    # Query all metric groups and their associated metrics
    metric_groups = db.query(MetricGroup).join(Metric).all()

    # Dictionary to hold grouped metrics
    grouped_metrics = {}

    # Loop through each metric group and their metrics
    for group in metric_groups:
        group_name = group.name  # Get the group name
        group_description = group.description  # Get the group description

        # Initialize the group if it's not in the dictionary
        if group_name not in grouped_metrics:
            grouped_metrics[group_name] = {
                "group_description": group_description if group_description else "No description",
                "metrics": []
            }

        # Add metrics belonging to this group
        for metric in group.metrics:
            grouped_metrics[group_name]["metrics"].append({
                "name": metric.name,
                "description": metric.description if metric.description else "No description"
            })

    return grouped_metrics
