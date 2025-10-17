from __future__ import annotations
from app.models.metric import MetricDefinition
from app.utils.database import SessionLocal

CORE_METRICS = [
    dict(metric_id="F",  display_name="Interactions per minute",
         description="Count of agent actions per minute in the agent window.",
         formula_tex="F = N / (T/60)", required_fields=["t","agent"]),
    dict(metric_id="D",  display_name="Mean action duration",
         description="Average atomic action duration (s).",
         formula_tex="D = \\frac{1}{N}\\sum d_i", required_fields=["duration_s|latency_ms"]),
    dict(metric_id="HCL",display_name="Human-centeredness (RT scaled)",
         description="Proxy for cognitive load via reaction time vs rt_max.",
         formula_tex="HCL = 1 - \\overline{RT}/RT_{max}", required_fields=["duration_s|latency_ms"]),
    dict(metric_id="Tr", display_name="Trust proxy (error rate)",
         description="1 - errors / labeled, incl. explicit error events.",
         formula_tex="Tr = 1 - \\frac{errors}{N_{labeled}}", required_fields=["correct|event_type=error"]),
    dict(metric_id="A",  display_name="Adaptability",
         description="Relative improvement late vs early; tanh-bounded.",
         formula_tex="A = \\tanh\\left(\\frac{Acc_{late}-Acc_{early}}{Acc_{early}}\\right)",
         required_fields=["correct"]),
    dict(metric_id="S",  display_name="Surrogate similarity",
         description="exp(-KL(P_h||P_s)) over action distributions; fallback action match.",
         formula_tex="S = e^{-KL(P_h||P_s)}",
         required_fields=["probs|surrogate_probs|surrogate_action"]),
    dict(metric_id="EL", display_name="Effort/Efficiency Loss",
         description="Relative excess time vs baseline.",
         formula_tex="EL = (T_{actual}-T_{baseline})/T_{baseline}",
         required_fields=["t","baseline_s"]),
    dict(metric_id="EfficiencyScore", display_name="EfficiencyScore",
         description="1/(1+EL) with off-role penalty & progress bonus (clipped).",
         formula_tex=("ES = \\mathrm{clip}\\left(\\frac{1}{1+EL}"
                      "\\times(1-w_{off}r_{off})\\times(1+w_{prog}r_{prog})\\right)"),
         required_fields=["EL|off_role_action|event_type=progress"]),
]

def seed_core_definitions() -> None:
    """Idempotent upsert of Core v1 metric definitions."""
    db = SessionLocal()
    try:
        for m in CORE_METRICS:
            row = db.get(MetricDefinition, m["metric_id"])
            if row:
                row.display_name = m["display_name"]
                row.description = m["description"]
                row.formula_tex = m["formula_tex"]
                row.required_fields = m["required_fields"]
            else:
                db.add(MetricDefinition(**m))
        db.commit()
    finally:
        db.close()
