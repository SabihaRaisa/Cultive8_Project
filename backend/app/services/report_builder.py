
from app.services.database import get_analysis_report
from app.services.correlation import correlate_findings


def build_analysis_report(run_id):
    """
    Build a consolidated report for one analysis run.

    Retrieves saved database findings, merges related findings
    across chunks, and calculates report statistics.
    """

    # Retrieve saved analysis data from SQLite.
    database_report = get_analysis_report(run_id)

    if not database_report or not database_report.get("run"):
        raise ValueError(f"Analysis run {run_id} was not found.")

    run = database_report["run"]
    chunks = database_report.get("chunks", [])
    raw_findings = database_report.get("findings", [])

    # Merge repeated findings across different chunks.
    correlated_findings = correlate_findings(raw_findings)

    # Count findings by severity after correlation.
    severity_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0
    }

    for finding in correlated_findings:
        severity = finding.get("severity", "Low")

        if severity in severity_counts:
            severity_counts[severity] += 1

    # Calculate chunk processing statistics.
    completed_chunks = sum(
        1 for chunk in chunks
        if chunk.get("status") == "completed"
    )

    failed_chunks = sum(
        1 for chunk in chunks
        if chunk.get("status") == "failed"
    )

    total_processing_time = round(
        sum(
            chunk.get("processing_time") or 0
            for chunk in chunks
        ),
        3
    )

    total_prompt_tokens = sum(
        chunk.get("prompt_tokens") or 0
        for chunk in chunks
    )

    total_output_tokens = sum(
        chunk.get("output_tokens") or 0
        for chunk in chunks
    )

    return {
        "run": run,

        "summary": {
            "total_chunks": len(chunks),
            "completed_chunks": completed_chunks,
            "failed_chunks": failed_chunks,
            "raw_findings": len(raw_findings),
            "total_findings": len(correlated_findings),
            "severity_counts": severity_counts,
            "processing_time_seconds": total_processing_time,
            "prompt_tokens": total_prompt_tokens,
            "output_tokens": total_output_tokens
        },

        "findings": correlated_findings,

        "chunks": chunks
    }
