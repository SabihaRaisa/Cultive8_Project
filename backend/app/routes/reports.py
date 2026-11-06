
from fastapi import APIRouter, HTTPException

from app.services.report_builder import build_analysis_report

router = APIRouter(prefix="/api/reports", tags=["Analysis Reports"])


@router.get("/{run_id}")
def get_report(run_id: int):

    if run_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Run ID must be a positive number."
        )

    try:
        report = build_analysis_report(run_id)

        return {
            "status": "success",
            "message": "Analysis report retrieved successfully.",
            "data": report
        }

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis run {run_id} was not found."
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the analysis report."
        )
