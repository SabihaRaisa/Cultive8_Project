
from app.services.ollama_client import OllamaClient


def main():
    client = OllamaClient()

    print("Checking Ollama connection...")

    status = client.check_connection()

    print(status)

    if not status["connected"]:
        print("Ollama connection failed.")
        return

    if not status["model_available"]:
        print("Required model is not available.")
        return

    print("\nTesting local AI generation...")

    result = client.generate(
        'Return JSON with one key: status. '
        'Its value must be "working".'
    )

    print(result)

    if result["success"]:
        print("\nSUCCESS: Local AI generation works!")
    else:
        print("\nAI generation failed.")


if __name__ == "__main__":
    main()
