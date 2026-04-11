from httpx import HTTPStatusError

from core.ServiceResult import ServiceResult
from infrastucture.llm_client import MathAIClient


class AIService:
    def __init__(self, llm_client: MathAIClient):
        self.llm_client = llm_client

    async def get_show_solution(self, expression: str, language: str = "ru"):
        """
        Получает пошаговое решение математического выражения.
        """
        try:
            system_prompt = f"Ты математический помощник. Реши задачу на языке {language} и покажи решение пошагово."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": expression}
            ]

            response_text = await self.llm_client.chat_completion(messages)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str):
        """
        Генерирует похожие математические выражения и их решения.
        """
        try:
            system_prompt = """You are a math problem generator. You will receive one example of an equation, inequality, or other math problem. Your task is to generate ONE new problem that is similar in topic, difficulty, and concept – just like different exercises from the same school lesson. Do NOT simply change the numbers; vary the form while keeping the underlying mathematical structure.
Strictly follow these formatting rules:
- Use '*' for multiplication (e.g., 5 * x, 4 * 3).
- Use '^' or '**' for exponents (e.g., 2^4, x**2).
- Always use 'x' as the variable (no 'a', 'y', etc.).
- For trigonometric functions, put degrees in parentheses: sin(30), cos(45), tg(90), ctg(0).
- If the input is unsolvable (e.g., division by zero, invalid syntax), output NOTHING (empty response).

Output ONLY the generated problem as a single line of text. Do not add explanations, labels, or extra characters.

Input example: 3 * x + 5 = 14
Output: 2 * x - 4 = 6

Input example: x^2 - 9 = 0
Output: x**2 - 16 = 0

Input example: sin(30) + cos(60)
Output: sin(45) + cos(45)

Input example: 5 / 0 = x
Output: 0 / 7 = x

Now generate a similar problem for the following input:
{{INPUT}}"
"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": expression}
            ]

            response_text = await self.llm_client.chat_completion(messages)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')