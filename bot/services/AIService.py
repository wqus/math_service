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
            full_prompt = f"""Ответ должен быть на языке: {language}

Ты — математический репетитор. Реши уравнение или выражение ПОШАГОВО.

Правила:
1. Покажи КАЖДЫЙ шаг решения с объяснением
2. Используй понятные математические обозначения
3. В конце напиши финальный ответ

Вот выражение: {expression}

Формат вывода:
Шаг 1: [действие и объяснение]
Шаг 2: [действие и объяснение]
...
Ответ: [конечный результат]"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str = "ru") -> ServiceResult:
        """
        Генерирует похожее математическое выражение для самостоятельного решения.
        """
        try:
            full_prompt = f"""Ответ должен быть на языке: {language}

Ты — генератор математических задач. Создай ОДНУ новую задачу, похожую на пример.

Правила:
- Сохрани тип задачи (уравнение, неравенство, арифметика, тригонометрия и т.д.)
- Сохрани уровень сложности
- Измени числа и форму, но не меняй структуру
- Используй переменную 'x' если она была в примере
- Используй '*' для умножения: 5 * x, 4 * 3
- Используй '^' для степеней: 2^4, x^2
- Для тригонометрии: sin(30), cos(45), tg(90)

Выведи ТОЛЬКО сгенерированную задачу, ничего лишнего.

Пример: {expression}
Похожая задача:"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')