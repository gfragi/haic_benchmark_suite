import io
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from minio import Minio, S3Error
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult
# from app.services.agg_metrics import calculate_metrics_for_group
from app.utils.minio_utils import get_minio_client

router = APIRouter()

load_dotenv()

minio_client = get_minio_client()


# Fetch Evaluation Results grouped by configuration ID
@router.get("/{configuration_id}")
async def get_evaluation_results(configuration_id: int, db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).filter(EvaluationResult.configuration_id == configuration_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this configuration")
    return results

# Fetch specific Evaluation Result
@router.get("/{configuration_id}/{result_id}")
async def get_evaluation_result(configuration_id: int, result_id: int, db: Session = Depends(get_db)):
    # Fetch the result metadata from the database
    result = db.query(EvaluationResult).filter(
        EvaluationResult.configuration_id == configuration_id,
        EvaluationResult.id == result_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="No result found for this configuration and result ID")

    if not result.result_minio_path:
        raise HTTPException(status_code=500, detail="Result MinIO path is missing or not stored")

    # Fetch the result from MinIO using the stored path
    try:
        result_object = minio_client.get_object(os.getenv("MINIO_BUCKET"), result.result_minio_path)
        result_data = json.load(io.BytesIO(result_object.read()))
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result from MinIO: {str(e)}")

    return result_data



# Fetch Evaluation Results for a specific group of metrics
@router.get("/{configuration_id}/group/{group_name}")
async def get_evaluation_results_by_group(configuration_id: int, group_name: str, db: Session = Depends(get_db)):
    # Fetch the evaluation results metadata for this configuration
    results = db.query(EvaluationResult).filter(
        EvaluationResult.configuration_id == configuration_id
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this configuration")

    # Initialize an empty dictionary to hold results for the specified group
    group_results = {}

    # Iterate over each result and fetch the group-specific data from MinIO
    for result in results:
        # Check if result_minio_path is None or empty before trying to fetch from MinIO
        if not result.result_minio_path:
            raise HTTPException(status_code=500, detail=f"Result MinIO path is missing for result ID {result.id}")

        try:
            # Fetch the result from MinIO using the stored path
            result_object = minio_client.get_object(os.getenv("MINIO_BUCKET"), result.result_minio_path)
            result_data = json.load(io.BytesIO(result_object.read()))

            aggregates = result_data.get("aggregates") or {}
            by_group = aggregates.get("by_group") or {}
            if group_name in by_group:
                group_results[result.id] = by_group[group_name]

        except AttributeError:
            # Handle AttributeError if result_minio_path is invalid
            raise HTTPException(status_code=500, detail=f"Invalid MinIO path for result ID {result.id}")

        except S3Error as e:
            # Handle S3Error related to MinIO
            raise HTTPException(status_code=500, detail=f"Error fetching result from MinIO: {str(e)}")

    if not group_results:
        raise HTTPException(status_code=404, detail="No results found for the specified group")

    return group_results
