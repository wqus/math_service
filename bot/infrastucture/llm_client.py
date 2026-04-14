import httpx
import logging

logger = logging.getLogger(__name__)


class MathAIClient:
    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url + "/api/chat"
        self.timeout = httpx.Timeout(timeout)
        self.client = httpx.AsyncClient(timeout=self.timeout, limits=httpx.Limits(max_connections=100))
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def chat_completion(self, messages: list, model: str = "qwen-2.5:3b", temperature: float = 0.25) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }


    async def close(self):
        await self.client.aclose()