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

ВАЖНЫЕ ПРАВИЛА ФОРМАТИРОВАНИЯ:
- НЕ ИСПОЛЬЗУЙ LaTeX (никаких \\(, \\[, $$, \\) и т.д.)
- НЕ ИСПОЛЬЗУЙ обратные слеши
- Используй обычный текст и символы: =, +, -, *, /, ^
- Для дробей используй / (например, 21/7)
- Каждый шаг пиши с новой строки
- Используй обычные скобки ( )

Правила решения:
1. Покажи КАЖДЫЙ шаг решения с объяснением
2. Используй понятные математические обозначения
3. В конце напиши финальный ответ

Вот выражение: {expression}

Пример правильного форматирования:
Шаг 1: Разделим обе части уравнения на 7
7x/7 = 21/7
x = 21/7

Шаг 2: Выполним деление
x = 3

Ответ: x = 3

Теперь реши это выражение:"""

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

ВАЖНЫЕ ПРАВИЛА ФОРМАТИРОВАНИЯ:
- НЕ ИСПОЛЬЗУЙ LaTeX (никаких \\(, \\[, $$, \\) и т.д.)
- НЕ ИСПОЛЬЗУЙ обратные слеши
- Используй обычный текст и символы: =, +, -, *, /, ^
- Используй '*' для умножения: 5 * x, 4 * 3
- Используй '^' для степеней: 2^4, x^2
- Для тригонометрии: sin(30), cos(45), tg(90)

Правила:
- Сохрани тип задачи (уравнение, неравенство, арифметика, тригонометрия и т.д.)
- Сохрани уровень сложности
- Измени числа и форму, но не меняй структуру
- Используй переменную 'x' если она была в примере

Выведи ТОЛЬКО сгенерированную задачу, ничего лишнего.

Пример правильного форматирования:
Вход: 3*x + 5 = 14
Выход: 2*x - 4 = 6

Вход: x^2 - 9 = 0
Выход: x^2 - 16 = 0

Теперь создай задачу для примера: {expression}
Похожая задача:"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')