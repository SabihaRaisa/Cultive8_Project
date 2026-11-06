
from app.services.ollama_client import OllamaClient
from app.services.token_counter import TokenCounter
from app.services.ai_analyzer import AIAnalyzer

from app.services.database import (
    initialize_database,
    create_analysis_run,
    get_analysis_report
)


def main():

    print("Initializing AI analyzer...")

    # Initialize database
    initialize_database()

    # Initialize local AI
    client = OllamaClient()
    tokenizer = TokenCounter()

    analyzer = AIAnalyzer(
        ollama_client=client,
        token_counter=tokenizer
    )

    # Sample server logs
    sample_chunk = {
        "chunk_number": 1,
        "lines": [
            {"line_number": 5, "content": "Failed login from 192.168.1.10"},
            {"line_number": 6, "content": "Failed login from 192.168.1.10"},
            {"line_number": 7, "content": "Failed login from 192.168.1.10"},
            {"line_number": 8, "content": "Failed login from 192.168.1.10"},
            {"line_number": 12, "content": "Failed login from 192.168.1.10"}
        ]
    }

    # Create database analysis run
    run_id = create_analysis_run("sample_security.log")

    print("\nAnalysis Run ID:", run_id)

    print("\nSending sample logs to local AI...")

    # Analyze and automatically save results
    result = analyzer.analyze_chunks(
        [sample_chunk],
        run_id=run_id
    )

    print("\n========== AI ANALYSIS RESULT ==========")
    print(result)

    # Retrieve saved database report
    print("\n========== SAVED DATABASE REPORT ==========")

    report = get_analysis_report(run_id)

    print(report)

    # Verify persistence
    assert report is not None, "Database report not found!"
    assert len(report["chunks"]) == 1, "Chunk was not saved!"

    print("\nSUCCESS: AI analysis and SQLite persistence completed!")


if __name__ == "__main__":
    main()
