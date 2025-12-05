from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import EvaluationResult

def aggregate_evaluation_results_by_date(db: Session):
    """Aggregate evaluation results by date. Currently returns basic count data."""
    try:
        # Get basic counts by date for now (metrics are stored in MinIO JSON files)
        results = db.query(
            EvaluationResult.evaluation_date,
            func.count(EvaluationResult.id).label('evaluation_count')
        ).group_by(EvaluationResult.evaluation_date).all()

        # Convert to expected format
        return [
            {
                "date": result.evaluation_date.isoformat() if result.evaluation_date else None,
                "count": result.evaluation_count,
                "avg_accuracy": None,  # Would need to read from MinIO files
                "avg_response_time": None  # Would need to read from MinIO files
            }
            for result in results
        ]
    except Exception as e:
        # Return empty list on error to prevent crashes
        return []


def get_evaluation_summary(db: Session):
    """Get basic evaluation summary."""
    try:
        total_count = db.query(EvaluationResult).count()
        return [
            "Evaluation Summary",
            f"Total Evaluations: {total_count}",
            "Note: Detailed metrics stored in MinIO JSON files"
        ]
    except Exception as e:
        return ["Evaluation Summary", "Error retrieving data"]
