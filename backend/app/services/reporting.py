from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import EvaluationResult

def aggregate_evaluation_results_by_date(db: Session):
    return db.query(
        EvaluationResult.evaluation_date,
        func.avg(EvaluationResult.metrics['Prediction Accuracy'].as_float()).label('avg_accuracy'),
        func.avg(EvaluationResult.metrics['Response Time'].as_float()).label('avg_response_time')
    ).group_by(EvaluationResult.evaluation_date).all()


def get_evaluation_summary(db: Session):
    return [
        "Evaluation Summary",
        f"Total Evaluations: {db.query(EvaluationResult).count()}",
        f"Average Accuracy: {db.query(func.avg(EvaluationResult.metrics['Prediction Accuracy'].as_float())).scalar()}",
        f"Average Response Time: {db.query(func.avg(EvaluationResult.metrics['Response Time'].as_float())).scalar()}",
    ]
