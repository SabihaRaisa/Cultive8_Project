
import time

from app.services.security_prompt import build_analysis_prompt
from app.services.finding_validator import validate_findings
from app.services.database import (
    save_chunk_result,
    update_analysis_status
)


class AIAnalyzer:

    def __init__(
        self,
        ollama_client,
        token_counter,
        max_context_tokens=2048,
        output_tokens=300,
        safety_tokens=100,
        max_retries=1
    ):
        self.client = ollama_client
        self.token_counter = token_counter

        self.max_context_tokens = max_context_tokens
        self.output_tokens = output_tokens
        self.safety_tokens = safety_tokens
        self.max_retries = max_retries

    def _get_log_text(self, chunk):

        lines = chunk.get("lines", [])

        if lines:
            return "\n".join(
                f"Line {item['line_number']}: {item['content']}"
                for item in lines
            )

        return chunk.get("text", "")

    def _get_line_numbers(self, chunk):

        return [
            item["line_number"]
            for item in chunk.get("lines", [])
        ]

    def analyze_chunk(self, chunk, saved_context=""):

        log_text = self._get_log_text(chunk)
        valid_lines = self._get_line_numbers(chunk)

        if not log_text.strip():
            return {
                "success": False,
                "chunk_number": chunk.get("chunk_number"),
                "findings": [],
                "processing_time": 0,
                "error": "Empty log chunk."
            }

        prompt = build_analysis_prompt(
            log_text=log_text,
            saved_context=saved_context
        )

        prompt_tokens = self.token_counter.count(prompt)

        max_prompt_tokens = (
            self.max_context_tokens
            - self.output_tokens
            - self.safety_tokens
        )

        if prompt_tokens > max_prompt_tokens:
            return {
                "success": False,
                "chunk_number": chunk.get("chunk_number"),
                "findings": [],
                "processing_time": 0,
                "prompt_tokens": prompt_tokens,
                "error": (
                    f"Prompt too large: {prompt_tokens} tokens. "
                    f"Maximum allowed: {max_prompt_tokens}."
                )
            }

        for attempt in range(self.max_retries + 1):

            start_time = time.perf_counter()

            result = self.client.generate(prompt)

            elapsed = round(
                time.perf_counter() - start_time, 3
            )

            if not result.get("success"):

                if attempt < self.max_retries:
                    continue

                return {
                    "success": False,
                    "chunk_number": chunk.get("chunk_number"),
                    "findings": [],
                    "processing_time": elapsed,
                    "prompt_tokens": prompt_tokens,
                    "error": result.get(
                        "error", "AI request failed."
                    )
                }

            validation = validate_findings(
                result.get("response", ""),
                valid_lines
            )

            if not validation["success"]:

                return {
                    "success": False,
                    "chunk_number": chunk.get("chunk_number"),
                    "findings": [],
                    "processing_time": elapsed,
                    "prompt_tokens": prompt_tokens,
                    "output_tokens": result.get("eval_count", 0),
                    "error": validation.get("error")
                }

            return {
                "success": True,
                "chunk_number": chunk.get("chunk_number"),
                "findings": validation["findings"],
                "summary": validation.get("summary", ""),
                "processing_time": elapsed,
                "prompt_tokens": prompt_tokens,
                "output_tokens": result.get("eval_count", 0)
            }

    def analyze_chunks(self, chunks, run_id=None):

        all_findings = []
        chunk_results = []

        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks, start=1):

            print(
                f"\nAnalyzing chunk {index}/{total_chunks}..."
            )

            result = self.analyze_chunk(chunk)

            # Save immediately after each AI call.
            if run_id is not None:
                save_chunk_result(run_id, result)

            chunk_results.append(result)

            if result["success"]:

                all_findings.extend(result["findings"])

                print(
                    f"Completed chunk {index}: "
                    f"{len(result['findings'])} findings"
                )

            else:

                print(
                    f"Chunk {index} failed: "
                    f"{result.get('error')}"
                )

        completed = sum(
            1 for item in chunk_results
            if item["success"]
        )

        failed = total_chunks - completed

        # Update overall database status.
        if run_id is not None:

            if failed == 0:
                status = "completed"

            elif completed == 0:
                status = "failed"

            else:
                status = "partial"

            update_analysis_status(run_id, status)

        return {
            "total_chunks": total_chunks,
            "completed_chunks": completed,
            "failed_chunks": failed,
            "findings": all_findings,
            "chunk_results": chunk_results
        }
