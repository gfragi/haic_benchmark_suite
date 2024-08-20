from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services.reporting import aggregate_evaluation_results_by_date, get_evaluation_summary
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

router = APIRouter()

@router.get("/aggregate-by-date")
def get_aggregated_results(db: Session = Depends(get_db)):
    results = aggregate_evaluation_results_by_date(db)
    return results


@router.get("/time-series-data")
def get_time_series_data(db: Session = Depends(get_db)):
    data = aggregate_evaluation_results_by_date(db)
    time_series = {
        "dates": [result.evaluation_date for result in data],
        "avg_accuracy": [result.avg_accuracy for result in data],
        "avg_response_time": [result.avg_response_time for result in data],
    }
    return time_series


@router.get("/generate-report")
def generate_pdf_report(db: Session = Depends(get_db)):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Human-AI Collaboration Evaluation Report")

    summary = get_evaluation_summary(db)
    y = 700
    for line in summary:
        c.drawString(100, y, line)
        y -= 20

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(buffer, media_type='application/pdf')
