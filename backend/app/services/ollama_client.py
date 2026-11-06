
import json
import urllib.request
import urllib.error


class OllamaClient:

    def __init__(
        self,
        model="qwen2.5:0.5b-instruct",
        base_url="http://localhost:11434",
        timeout=180
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_connection(self):
        url = f"{self.base_url}/api/tags"

        try:
            with urllib.request.urlopen(
                url, timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            models = [
                item["name"]
                for item in data.get("models", [])
            ]

            available = any(
                name == self.model
                or name.startswith(self.model + ":")
                for name in models
            )

            return {
                "connected": True,
                "model_available": available,
                "models": models
            }

        except Exception as error:
            return {
                "connected": False,
                "model_available": False,
                "error": str(error)
            }

    def generate(self, prompt):

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "num_ctx": 2048,
                "num_predict": 300,
                "temperature": 0
            }
        }

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            return {
                "success": True,
                "response": result.get("response", ""),
                "total_duration": result.get("total_duration"),
                "eval_count": result.get("eval_count")
            }

        except urllib.error.HTTPError as error:
            return {
                "success": False,
                "error": f"Ollama HTTP error: {error.code}"
            }

        except Exception as error:
            return {
                "success": False,
                "error": str(error)
            }
