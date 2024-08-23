import os
import tempfile
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
from app.utils.log_templates import generate_log

router = APIRouter()


class GenerateLogRequest(BaseModel):
    app_type: str
    count: int



@router.get("/generate")
def generate_log_endpoint(
    app_type: str = Query("radiologist", description="Type of application to generate logs for"),
    count: int = Query(100, description="Number of log entries to generate"),
    start_date: str = Query("2024-02-10T13:00:00Z", description="Start date of the log period"),
    end_date: str = Query("2024-05-10T13:00:00Z", description="End date of the log period"),
    model_version_range: str = Query("1.0.0 - 3.0.0", description="Range of model versions")
):

    logs = [generate_log(app_type, start_date, end_date, model_version_range) for _ in range(count)]

# Save logs to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, 'w') as f:
        json.dump(logs, f)

    return logs



@router.get("/download/")
async def download_log(file_path: str):
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="generated_logs.json", media_type='application/json')
    else:
        raise HTTPException(status_code=404, detail="File not found")
