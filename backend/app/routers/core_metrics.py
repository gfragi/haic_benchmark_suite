import json
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.core_metrics import compute_core_v1_for_run
from metrics_core.interaction_metrics import compute_metrics, compute_metrics_by_agent

router = APIRouter()

@router.post("/from-run/{run_id}")
def compute_from_run(
    run_id: str,
    rt_max: float = Query(5.0, description="Upper cap for reaction time scaling"),
    baseline_s: Optional[float] = Query(None, description="Baseline seconds for EL"),
):
    try:
        artifact, minio_path = compute_core_v1_for_run(run_id, rt_max=rt_max, baseline_s=baseline_s)
        return {"artifact": artifact, "minio_path": minio_path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Core-v1 compute failed: {e}")


@router.post("/core_v1/compute_from_artifact")
def core_v1_from_artifact(file: str = Query(..., description="Artifact JSON under metrics/")):
    path = METRICS_DIR / file
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        art = json.load(open(path))
        decisions = art.get("decisions", [])
        rt_max = art.get("params", {}).get("rt_max", 5.0)
        baseline_s = art.get("params", {}).get("baseline_s")
        out = compute_metrics(decisions=decisions, rt_max=rt_max, baseline_s=baseline_s)
        by_agent = compute_metrics_by_agent(decisions, rt_max=rt_max, baseline_s=baseline_s)
        return {"metrics": out, "by_agent": by_agent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")
