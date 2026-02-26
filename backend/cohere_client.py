import json
import requests
from config import Config

COHERE_URL = "https://api.cohere.com/v2/chat"


class CohereClient:
    def __init__(self) -> None:
        self.api_key = Config.COHERE_API_KEY
        self.model = Config.COHERE_MODEL

    def _request(self, messages, temperature=0.2, response_format=None):
        if not self.api_key:
            raise RuntimeError("COHERE_API_KEY is not configured")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        res = requests.post(
            COHERE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=180,
        )
        res.raise_for_status()
        data = res.json()
        return data.get("message", {}).get("content", [{}])[0].get("text", "").strip()

    def chat(self, system_prompt, user_prompt, temperature=0.2):
        return self._request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
