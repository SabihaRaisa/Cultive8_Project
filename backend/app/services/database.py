import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


# backend/data/security_analyzer.db
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
DATABASE_PATH = DATA_DIR / "security_analyzer.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the required database tables."""
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'running',
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS analyzed_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                chunk_number INTEGER NOT NULL,
                status TEXT NOT NULL,
                summary TEXT,
                processing_time REAL,
                prompt_tokens INTEGER,
                output_tokens INTEGER,
                error TEXT,
                saved_at TEXT NOT NULL,
                UNIQUE(run_id, chunk_number),
                FOREIGN KEY (run_id) REFERENCES analysis_runs(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                chunk_number INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                identifier TEXT NOT NULL,
                evidence TEXT NOT NULL,
                line_numbers TEXT NOT NULL,
                reason TEXT NOT NULL,
                suggested_action TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES analysis_runs(id)
            )
        """)


def create_analysis_run(file_name):
    """Create a new analysis record and return its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analysis_runs (file_name, status, created_at)
            VALUES (?, ?, ?)
            """,
            (
                file_name,
                "running",
                datetime.now(timezone.utc).isoformat()
            )
        )

        return cursor.lastrowid


def save_chunk_result(run_id, chunk_result):
    """Save one chunk's result and its findings."""
    chunk_number = chunk_result.get("chunk_number")

    if chunk_number is None:
        raise ValueError("Chunk result is missing chunk_number.")

    success = chunk_result.get("success", False)
    status = "completed" if success else "failed"

    with get_connection() as connection:

        # Save or update the chunk result.
        connection.execute(
            """
            INSERT INTO analyzed_chunks (
                run_id,
                chunk_number,
                status,
                summary,
                processing_time,
                prompt_tokens,
                output_tokens,
                error,
                saved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id, chunk_number) DO UPDATE SET
                status = excluded.status,
                summary = excluded.summary,
                processing_time = excluded.processing_time,
                prompt_tokens = excluded.prompt_tokens,
                output_tokens = excluded.output_tokens,
                error = excluded.error,
                saved_at = excluded.saved_at
            """,
            (
                run_id,
                chunk_number,
                status,
                chunk_result.get("summary", ""),
                chunk_result.get("processing_time"),
                chunk_result.get("prompt_tokens"),
                chunk_result.get("output_tokens"),
                chunk_result.get("error"),
                datetime.now(timezone.utc).isoformat()
            )
        )

        # Replace findings for this chunk to avoid duplicates
        # if the same chunk is saved again.
        connection.execute(
            """
            DELETE FROM findings
            WHERE run_id = ? AND chunk_number = ?
            """,
            (run_id, chunk_number)
        )

        for finding in chunk_result.get("findings", []):
            connection.execute(
                """
                INSERT INTO findings (
                    run_id,
                    chunk_number,
                    attack_type,
                    severity,
                    identifier,
                    evidence,
                    line_numbers,
                    reason,
                    suggested_action
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    chunk_number,
                    finding["attack_type"],
                    finding["severity"],
                    finding["identifier"],
                    finding["evidence"],
                    json.dumps(finding["line_numbers"]),
                    finding["reason"],
                    finding["suggested_action"]
                )
            )


def update_analysis_status(run_id, status):
    """Update the overall analysis status."""
    allowed_statuses = {"running", "completed", "failed", "partial"}

    if status not in allowed_statuses:
        raise ValueError("Invalid analysis status.")

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = ?
            WHERE id = ?
            """,
            (status, run_id)
        )


def get_analysis_report(run_id):
    """Retrieve a saved analysis and all its findings."""
    with get_connection() as connection:

        run = connection.execute(
            "SELECT * FROM analysis_runs WHERE id = ?",
            (run_id,)
        ).fetchone()

        if run is None:
            return None

        chunks = connection.execute(
            """
            SELECT * FROM analyzed_chunks
            WHERE run_id = ?
            ORDER BY chunk_number
            """,
            (run_id,)
        ).fetchall()

        findings = connection.execute(
            """
            SELECT * FROM findings
            WHERE run_id = ?
            ORDER BY chunk_number, id
            """,
            (run_id,)
        ).fetchall()

        return {
            "run": dict(run),
            "chunks": [dict(chunk) for chunk in chunks],
            "findings": [
                {
                    **dict(finding),
                    "line_numbers": json.loads(finding["line_numbers"])
                }
                for finding in findings
            ]
        }