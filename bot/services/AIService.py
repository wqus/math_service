from httpx import HTTPStatusError

from core.ServiceResult import ServiceResult
from infrastucture.llm_client import MathAIClient


class AIService:
    def __init__(self, llm_client: MathAIClient):
        self.llm_client = llm_client

    async def get_show_solution(self, expression: str, language: str = "ru") -> ServiceResult:
        """
        Получает пошаговое решение математического выражения.
        """
        try:
            system_prompt = f"""You are a math solver that shows ONLY the essential solution steps – extremely compressed, minimal, just the core transformations. Do NOT add explanations, comments, or extra text. Use short equations and arrows (->) to show progression.

Input: a math problem (equation, inequality, trig expression, etc.). Output: the solution steps in the same language as {language} (RU or EN). Keep steps to absolute minimum (e.g., 2–4 lines). If unsolvable, output nothing.

Formatting rules:
- Use '*' for multiplication (5 * x, 4 * 3).
- Use '^' or '**' for exponents (2^4, x**2).
- Use 'x' as the variable.
- Degrees in parentheses: sin(30), cos(45).

Examples (EN):
Input: 3*x + 5 = 14
Output: 
3*x + 5 = 14
3*x = 9
x = 3

Input: x^2 - 9 = 0
Output:
x^2 = 9
x = 3 or x = -3

Input: sin(30) + cos(60)
Output:
0.5 + 0.5 = 1

Input (RU):
Пример: 2*x - 4 = 6
Вывод:
2*x - 4 = 6
2*x = 10
x = 5

Now generate a minimal solution for this problem in {language}:
{{INPUT}}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": expression}
            ]

            response_text = await self.llm_client.chat_completion(messages)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str)-> ServiceResult:
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
