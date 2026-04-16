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
            full_prompt = f"""You are a math problem generator. Analyze the input type and generate ONE new problem of the SAME type.

**TYPE DETECTION RULES:**
- If input has '=', '<', '>', '<=', '>=' → generate equation/inequality (keep the same variable, use 'x' if present)
- If input has only numbers and operators (+, -, *, /, ^, sin, cos, etc.) → generate arithmetic/trig expression (NO variable)
- If input has 'x' → generate with 'x'
- If input has NO 'x' → generate with NO variable

**FORMATTING RULES:**
- Use '*' for multiplication: 5 * x, 4 * 3
- Use '^' or '**' for exponents: 2^4, x**2
- Degrees in parentheses: sin(30), cos(45), tg(90)
- Keep inequality signs: <, >, <=, >=

**OUTPUT:** ONLY the generated expression, nothing else. If unsolvable, output NOTHING.

**EXAMPLES:**

Equation with x:
Input: 3*x + 5 = 14
Output: 2*x - 4 = 6

Equation with x (different form):
Input: x^2 - 9 = 0
Output: x**2 - 16 = 0

Inequality:
Input: 2*x + 3 > 7
Output: 3*x - 1 < 11

Simple arithmetic (no variable):
Input: 5 + 3
Output: 7 + 2

Trigonometry (no variable):
Input: sin(30) + cos(60)
Output: sin(45) + cos(45)

Trigonometry with x:
Input: sin(x) = 0.5
Output: cos(x) = 0.5

Multiplication:
Input: 5 * 4
Output: 6 * 3

Division:
Input: 12 / 4
Output: 20 / 5

Mixed operators:
Input: (3 + 5) * 2
Output: (4 + 6) * 3

Unsolvable (return empty):
Input: 5 / 0 = x
Output: 

Now generate a similar problem for this input:
{expression}"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str) -> ServiceResult:
        """
        Генерирует похожие математические выражения и их решения.
        """
        try:
            full_prompt = f"""You are a math problem generator. You will receive one example of an equation, inequality, or other math problem. Your task is to generate ONE new problem that is similar in topic, difficulty, and concept – just like different exercises from the same school lesson. Do NOT simply change the numbers; vary the form while keeping the underlying mathematical structure.

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
Output: 

Now generate a similar problem for the following input:
{expression}"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')