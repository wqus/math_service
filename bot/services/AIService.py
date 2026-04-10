from httpx import HTTPStatusError

from core.ServiceResult import ServiceResult
from infrastucture.llm_client import MathAIClient


class AIService:
    def __init__(self, llm_client: MathAIClient):
        self.llm_client = llm_client

    async def get_show_solution(self, ex: str, language: str = "ru"):
        try:
            system_prompt = f"Ты математический помощник. Реши задачу на языке {language} и покажи решение пошагово."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ex}
            ]

            response_text = await self.llm_client.chat_completion(messages)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception :
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, ex: str, language: str):
        try:
            system_prompt = f"Ты математический помощник. Сгенерируй похожие на переданное выражение три других {language} и покажи решение пошагово."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ex}
            ]

            response_text = await self.llm_client.chat_completion(messages)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

