
from pathlib import Path


class LogReader:

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    @staticmethod
    def read_log_file(file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("Log file not found.")

        if path.stat().st_size > LogReader.MAX_FILE_SIZE:
            raise ValueError("File exceeds the 10 MB limit.")

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("Please upload a UTF-8 text file.")

        lines = []

        for number, text in enumerate(content.splitlines(), start=1):
            if text.strip():
                lines.append({
                    "line_number": number,
                    "content": text
                })

        if not lines:
            raise ValueError("The log file is empty.")

        return {
            "filename": path.name,
            "total_lines": len(lines),
            "lines": lines
        }
