from dataclasses import dataclass

from app.services.token_counter import TokenCounter


@dataclass
class ChunkBudget:
    """
    Token allocation for one AI request.

    The total must remain within the model's
    2,048-token context limit.
    """

    max_context_tokens: int = 2048

    prompt_tokens: int = 350
    saved_context_tokens: int = 250
    output_tokens: int = 300
    safety_tokens: int = 100

    @property
    def available_log_tokens(self):

        available = (
            self.max_context_tokens
            - self.prompt_tokens
            - self.saved_context_tokens
            - self.output_tokens
            - self.safety_tokens
        )

        if available <= 0:
            raise ValueError(
                "Token allocation leaves no room for log content."
            )

        return available


class LogChunker:
    """
    Splits log entries into tokenizer-based chunks.

    Original line numbers are preserved.
    Complete lines are kept together whenever possible.
    """

    def __init__(
        self,
        token_counter=None,
        budget=None
    ):

        self.token_counter = (
            token_counter or TokenCounter()
        )

        self.budget = budget or ChunkBudget()

        self.max_log_tokens = (
            self.budget.available_log_tokens
        )

    def _prepare_lines(self, lines):
        """
        Prepare log lines.

        Each input line should look like:
        {
            "line_number": 10,
            "content": "Failed login from 192.0.2.10"
        }
        """

        prepared = []

        for line in lines:

            line_number = line.get("line_number")
            content = line.get("content", "")

            if line_number is None:
                raise ValueError(
                    "Every log entry must have a line number."
                )

            content = str(content)

            if not content.strip():
                continue

            token_count = self.token_counter.count(content)

            # Normal-sized log entry:
            # Keep the entire entry together.
            if token_count <= self.max_log_tokens:

                prepared.append({
                    "line_number": line_number,
                    "content": content,
                    "part": 1,
                    "parts": 1
                })

                continue

            # Extremely long entry:
            # Split it only when it cannot fit in one chunk.
            pieces = self.token_counter.split_text(
                content,
                self.max_log_tokens
            )

            # Re-check decoded pieces. Tokenization after
            # decoding can differ slightly from the original.
            safe_pieces = []

            for piece in pieces:

                if (
                    self.token_counter.count(piece)
                    <= self.max_log_tokens
                ):
                    safe_pieces.append(piece)

                else:
                    # Smaller split for unusual tokenizer cases.
                    smaller = self.token_counter.split_text(
                        piece,
                        max(1, self.max_log_tokens // 2)
                    )

                    safe_pieces.extend(smaller)

            total_parts = len(safe_pieces)

            for part_number, piece in enumerate(
                safe_pieces,
                start=1
            ):

                prepared.append({
                    "line_number": line_number,
                    "content": piece,
                    "part": part_number,
                    "parts": total_parts
                })

        return prepared

    def chunk_logs(self, lines):
        """
        Build chunks while respecting the token budget.

        Returns a list of chunks.
        """

        if not lines:
            raise ValueError("No log entries were provided.")

        prepared_lines = self._prepare_lines(lines)

        if not prepared_lines:
            raise ValueError("No usable log entries were found.")

        chunks = []

        current_lines = []

        for line in prepared_lines:

            candidate = current_lines + [line]

            candidate_text = "\n".join(
                item["content"] for item in candidate
            )

            candidate_tokens = (
                self.token_counter.count(candidate_text)
            )

            if (
                candidate_tokens > self.max_log_tokens
                and current_lines
            ):

                chunks.append(
                    self._create_chunk(
                        len(chunks) + 1,
                        current_lines
                    )
                )

                current_lines = [line]

            else:
                current_lines = candidate

        # Save the final chunk.
        if current_lines:

            chunks.append(
                self._create_chunk(
                    len(chunks) + 1,
                    current_lines
                )
            )

        return chunks

    def _create_chunk(self, chunk_number, lines):

        combined_text = "\n".join(
            item["content"] for item in lines
        )

        return {
            "chunk_number": chunk_number,
            "token_count": self.token_counter.count(
                combined_text
            ),
            "line_count": len(lines),
            "lines": lines,
            "text": combined_text
        }