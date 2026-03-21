import os
from typing import Optional, Dict, List, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class InterpretRequest(BaseModel):
    pilot_tag: str
    metrics: Dict[str, Optional[float]]
    warnings: List[Dict[str, Any]] = []


class InterpretResponse(BaseModel):
    narrative: str


@router.post("/interpret", response_model=InterpretResponse, tags=["Interpretation"])
def interpret_metrics(req: InterpretRequest):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured on server")

    try:
        import anthropic
    except ImportError:
        raise HTTPException(status_code=503, detail="anthropic package not installed")

    metric_lines = "\n".join(
        f"  {k}: {v if v is not None else 'not available'}"
        for k, v in req.metrics.items()
    )
    warning_lines = "\n".join(
        f"  - {w.get('metric', '')}: {w.get('warning', str(w))}"
        for w in req.warnings
    ) or "  none"

    prompt = (
        f"You are interpreting Human-AI Collaboration metrics for a {req.pilot_tag} "
        f"pilot partner who is not technical.\n\n"
        f"Metrics:\n{metric_lines}\n\n"
        f"Warnings:\n{warning_lines}\n\n"
        "Write 3 short paragraphs: overall quality, what works well, what to improve. "
        "Use plain language, no formulas."
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return InterpretResponse(narrative=message.content[0].text)
