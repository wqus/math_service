from httpx import HTTPStatusError

from core.ServiceResult import ServiceResult
from infrastucture.llm_client import MathAIClient


class AIService:
    def __init__(self, llm_client: MathAIClient):
        self.llm_client = llm_client

    async def get_show_solution(self, expression: str, language: str = "ru") -> ServiceResult:
        try:
            # Собираем полный промпт
            full_prompt = f"""Solve this equation step by step. Return only the final answer in format 'x = number'.

    Equation: {expression}"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str = "ru") -> ServiceResult:
        try:
            full_prompt = f"""You are a math problem generator. Generate ONE new problem similar to the example.

    Example: {expression}

    Output ONLY the generated problem, nothing else."""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')