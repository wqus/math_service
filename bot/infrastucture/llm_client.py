import httpx
import logging

logger = logging.getLogger(__name__)

class MathAIClient:
    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url + "/api/generate"
        self.timeout = httpx.Timeout(timeout)
        self.client = httpx.AsyncClient(timeout=self.timeout, limits=httpx.Limits(max_connections=100))
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def chat_completion(self, messages: list, model: str = "qwen-2.5:3b", temperature: float = 0.) -> str:
        full_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                full_prompt += f"{content}\n\n"
            elif role == "user":
                full_prompt += f"Input: {content}\n\nOutput:"
        payload = {
            "model": model,
            "messages": full_prompt,
            "temperature": temperature,
            "stream": False
        }
        try:
            response = await self.client.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data['response']
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM HTTP error {e.response.status_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM ошибка при запросе: {e}")
            raise

    #Закрытие сессии
    async def close(self):
        await self.client.aclose()