# backend/app/routers/collab.py
from pathlib import Path
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.schemas.collab import (
    ComputeRequest, CollabMetricsResponse, MetricsOut, PerAgentMetrics, Decision
)
from app.services.core_metrics import compute_core_v1_for_run  # your run → artifact service
from metrics_core.interaction_metrics import compute_metrics, compute_metrics_by_agent

router = APIRouter(prefix="/collab", tags=["Collaboration Metrics"])
METRICS_DIR = Path("metrics")

def _pack_response(source: str, params: dict, metrics: dict, per_agent: dict) -> CollabMetricsResponse:
    by_agent = [PerAgentMetrics(agent=a, metrics=MetricsOut(**m)) for a, m in per_agent.items()]
    return CollabMetricsResponse(
        source=source,
        params=params,
        metrics=MetricsOut(**metrics),
        by_agent=by_agent,
    )

@router.post("/compute", response_model=CollabMetricsResponse)
def compute(req: ComputeRequest):
    try:
        m = compute_metrics(decisions=[d.dict() for d in req.decisions],
                            rt_max=req.rt_max, baseline_s=req.baseline_s)
        per = compute_metrics_by_agent([d.dict() for d in req.decisions],
                                       rt_max=req.rt_max, baseline_s=req.baseline_s)
        return _pack_response(
            source="payload",
            params={"rt_max": req.rt_max, "baseline_s": req.baseline_s},
            metrics=m,
            per_agent=per,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compute: {e}")

@router.post("/from-artifact", response_model=CollabMetricsResponse)
def compute_from_artifact(file: str = Query(..., description="metrics/*.json")):
    path = METRICS_DIR / file
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    try:
        art = json.loads(path.read_text())
        decisions: List[Decision] = [Decision(**d) for d in art.get("decisions", [])]
        params = art.get("params", {})
        rt_max = float(params.get("rt_max", 5.0))
        baseline_s = params.get("baseline_s")

        m = compute_metrics(decisions=[d.dict() for d in decisions], rt_max=rt_max, baseline_s=baseline_s)
        per = compute_metrics_by_agent([d.dict() for d in decisions], rt_max=rt_max, baseline_s=baseline_s)
        return _pack_response("artifact", {"rt_max": rt_max, "baseline_s": baseline_s}, m, per)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Malformed JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")

@router.post("/from-run/{run_id}", response_model=CollabMetricsResponse)
def compute_from_run(
    run_id: str,
    rt_max: float = Query(5.0, description="Upper cap for HCL scaling (sec)"),
    baseline_s: Optional[float] = Query(None, description="Baseline for EL"),
):
    try:
        artifact, _minio_path = compute_core_v1_for_run(run_id, rt_max=rt_max, baseline_s=baseline_s)
        decisions = [Decision(**d) for d in artifact.get("decisions", [])]
        m = compute_metrics(decisions=[d.dict() for d in decisions], rt_max=rt_max, baseline_s=baseline_s)
        per = compute_metrics_by_agent([d.dict() for d in decisions], rt_max=rt_max, baseline_s=baseline_s)
        return _pack_response("run", {"rt_max": rt_max, "baseline_s": baseline_s}, m, per)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collab compute failed: {e}")
