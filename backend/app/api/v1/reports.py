from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.report_service import ReportService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])


@router.get("/{analysis_id}/pdf")
def download_pdf_report(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and stream a formal forensic PDF report for an analysis."""
    pdf_buffer = ReportService.generate_pdf_report(db, analysis_id, current_user)
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Forensic_Report_{analysis_id[:8]}.pdf"}
    )


@router.get("/{analysis_id}/csv")
def download_csv_report(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and stream a machine-readable CSV export for an analysis."""
    csv_content = ReportService.generate_csv_report(db, analysis_id, current_user)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Forensic_Report_{analysis_id[:8]}.csv"}
    )
