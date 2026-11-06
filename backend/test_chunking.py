from app.services.token_counter import TokenCounter
from app.services.log_chunker import LogChunker, ChunkBudget


def main():

    print("\nLoading tokenizer...")

    counter = TokenCounter()

    # Small budget for testing so that we can
    # see multiple chunks without a huge test file.
    test_budget = ChunkBudget(
        max_context_tokens=512,
        prompt_tokens=80,
        saved_context_tokens=50,
        output_tokens=80,
        safety_tokens=50
    )

    chunker = LogChunker(
        token_counter=counter,
        budget=test_budget
    )

    sample_logs = [

        {
            "line_number": 1,
            "content": "2026-11-06 10:00:01 INFO Server started."
        },

        {
            "line_number": 2,
            "content": "2026-11-06 10:00:05 INFO User login successful."
        },

        {
            "line_number": 3,
            "content": "2026-11-06 10:00:08 WARNING Failed login from 192.0.2.15."
        },

        {
            "line_number": 4,
            "content": "2026-11-06 10:00:09 WARNING Failed login from 192.0.2.15."
        },

        {
            "line_number": 5,
            "content": "2026-11-06 10:00:10 ERROR Unauthorized access attempt."
        }
    ]

    # Add more entries to test chunk creation.
    for number in range(6, 31):

        sample_logs.append({
            "line_number": number,
            "content": (
                f"2026-11-06 10:01:{number:02d} "
                f"INFO Test log entry number {number}."
            )
        })

    print("Creating chunks...")

    chunks = chunker.chunk_logs(sample_logs)

    print("\n========== CHUNKING RESULTS ==========")

    print("Total input lines:", len(sample_logs))
    print("Total chunks:", len(chunks))
    print("Maximum log tokens:", chunker.max_log_tokens)

    for chunk in chunks:

        line_numbers = [
            item["line_number"]
            for item in chunk["lines"]
        ]

        print("\n----------------------------------")
        print("Chunk:", chunk["chunk_number"])
        print("Tokens:", chunk["token_count"])
        print("Lines:", line_numbers)
        print("Content:")
        print(chunk["text"])

        assert (
            chunk["token_count"] <= chunker.max_log_tokens
        ), "Chunk exceeded its token budget!"

    print("\nSUCCESS: All chunks fit within the token budget.")


if __name__ == "__main__":
    main()