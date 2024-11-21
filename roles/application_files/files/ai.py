import os
import httpx
from dotenv import load_dotenv
import time

# Załaduj zmienne środowiskowe
load_dotenv()

class AnthropicCompletion:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided or incorrectly set in environment variables")

    async def completion(self, messages: list, model: str = "claude-3-5-sonnet-20241022", retries: int = 3, delay: int = 5) -> dict:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        for attempt in range(retries):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url, headers=headers, json=payload)
                    if response.status_code == 529:
                        time.sleep(delay)
                        continue
                    response.raise_for_status()
                    return response.json()
                except httpx.RequestError as e:
                    if attempt == retries - 1:
                        raise
                except httpx.HTTPStatusError as e:
                    if attempt == retries - 1:
                        raise

