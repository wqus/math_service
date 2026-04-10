import httpx
import logging
from httpx import HTTPStatusError

logger = logging.getLogger(__name__)


class MathAIClient:
    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json'
        }

    async def chat_completion(self, prompt: str) -> dict:
        payload = {
            'model': 'qwen-2.5:3b',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.25
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=self.api_url, json=payload, headers=self.headers, timeout=self.timeout)

                response.raise_for_status()

                result = response.json()
                return {'success': True, 'content': result['choices'][0]['message']['content']}
        except HTTPStatusError as e:
            logger.error(f"Ошибка сервера: {e}")
            return {'success': False, 'content': ''}

        except Exception as e:
            logger.error(f"Ошибка сети: {e}")
            return {'success': False, 'content': ''}
