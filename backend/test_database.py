from app.services.database import (
    initialize_database,
    create_analysis_run,
    save_chunk_result,
    get_analysis_report,
    update_analysis_status
)


print("Initializing database...")
initialize_database()

print("Creating analysis run...")
run_id = create_analysis_run("sample_security.log")

print("Saving sample chunk and finding...")

sample_result = {
    "success": True,
    "chunk_number": 1,
    "summary": "Possible brute-force attack detected.",
    "processing_time": 9.679,
    "prompt_tokens": 477,
    "output_tokens": 134,
    "findings": [
        {
            "attack_type": "Possible brute-force attack",
            "severity": "High",
            "identifier": "192.168.1.10",
            "evidence": "Failed login attempts from 192.168.1.10",
            "line_numbers": [5, 8, 12],
            "reason": "Repeated failed login attempts from the same IP.",
            "suggested_action": "Review authentication activity."
        }
    ]
}

save_chunk_result(run_id, sample_result)
update_analysis_status(run_id, "completed")

print("\nRetrieving saved report...")
report = get_analysis_report(run_id)

print(report)

assert report is not None
assert report["run"]["file_name"] == "sample_security.log"
assert len(report["chunks"]) == 1
assert len(report["findings"]) == 1
assert report["findings"][0]["line_numbers"] == [5, 8, 12]

print("\nSUCCESS: Database persistence test passed!")