from sqlmodel import select
from app.utils.database import SessionLocal
from app.models.results import MetricGroup, Metric

GROUP_DESC = {
    1: "Measures how accurately the system achieves the intended task (correctness and quality of outputs).",
    2: "Measures speed and resource use: how quickly and efficiently the system delivers results.",
    3: "Measures how well the system adapts over time, learns from feedback, and improves.",
    4: "Measures the quality of human–AI teamwork: alignment, assistance, and joint outcomes.",
    5: "Measures safety, reliability, and user confidence while avoiding harmful behavior.",
    6: "Measures performance under distribution shifts, edge cases, and adversarial conditions.",
}

METRIC_DESC = {
    1: "Share of correct predictions (0–1).",
    2: "Positive predictive value of model outputs (0–1).",
    3: "Sensitivity: fraction of positives correctly found (0–1).",
    4: "End-to-end accuracy at the system level (0–1).",
    5: "Rate of accuracy improvement across versions or time.",
    6: "Time from input to model response (seconds).",
    7: "How much guidance accelerates learning or task success (0–1).",
    8: "Efficiency of information requests or queries (0–1).",
    9: "Compute / memory / bandwidth efficiency (0–1, higher = better).",
    10: "Elapsed time to complete the task (seconds).",
    11: "Speed/quality of fixing errors or refining outputs (0–1).",
    12: "Share of previously made errors that no longer occur (0–1).",
    13: "User or system’s ability to recall learned information (0–1).",
    14: "Observed impact of user feedback on model behavior (0–1).",
    15: "Overall capacity to adjust to new goals, data, or instructions (0–1).",
    16: "Effect that corrections have on subsequent outputs (0–1).",
    17: "Learning progress per unit time or interaction (0–1).",
    18: "Rate of meeting stated objectives or acceptance criteria (0–1).",
    19: "Agreement between human judgment and AI suggestion (0–1).",
    20: "Portion of steps where AI provides useful assistance (0–1).",
    21: "Quality of decisions made with AI vs without AI (0–1).",
    22: "Elapsed time from issue start to satisfactory resolution (seconds).",
    23: "Reduction in human effort compared to baseline (0–1 or %).",
    24: "User-reported or model-estimated confidence in outputs (0–1).",
    25: "Composite trust indicator derived from quality, transparency, and safety (0–1).",
    26: "Count of safety issues or policy violations (count).",
    27: "Service reliability / uptime / fault-free rate (0–1).",
    28: "Resistance to adversarial or worst-case inputs (0–1).",
    29: "Ability to maintain performance on new domains or distributions (0–1).",
}

def run():
    with SessionLocal() as s:
        # groups 
        for gid, desc in GROUP_DESC.items():
            mg = s.exec(select(MetricGroup).where(MetricGroup.id == gid)).first()
            if mg:
                mg.description = desc
        # metrics
        for mid, desc in METRIC_DESC.items():
            m = s.exec(select(Metric).where(Metric.id == mid)).first()
            if m:
                m.description = desc
        s.commit()

if __name__ == "__main__":
    run()