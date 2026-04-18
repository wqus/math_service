from bot.core.ServiceResult import ServiceResult
from bot.infrastucture.llm_client import MathAIClient


class AIService:
    def __init__(self, llm_client: MathAIClient):
        self.llm_client = llm_client

    async def get_show_solution(self, expression: str, language: str = "language: RU") -> ServiceResult:
        """
        Получает пошаговое решение математического выражения.
        """
        try:
            full_prompt = f"""Реши уравнение и покажи КАЖДЫЙ шаг как в школьной тетради.

    Язык пояснений: {language}

    ПРАВИЛА ОФОРМЛЕНИЯ (Telegram-friendly):
    - НЕ используй LaTeX, Markdown, HTML
    - НЕ используй обратные слеши
    - Используй обычные символы: = + - * / ^ ( )
    - Каждый шаг с новой строки
    - Минимум слов, максимум математики
    - Пояснения короткие (2-3 слова), только суть

    ФОРМАТ (строго соблюдай):
    7x = 21
    x = 21 / 7
    x = 3

    Ответ: x = 3

    Пример плохого оформления (ТАК НЕ ДЕЛАЙ):
    "Шаг 1: Разделим обе части уравнения на 7, получаем x = 21/7, затем выполняем деление и получаем x = 3" ← много слов

    Пример хорошего оформления (ДЕЛАЙ ТАК):
    7x = 21
    x = 21 / 7
    x = 3

    Ответ: x = 3

    Реши: {expression}

    Твой ответ (только решение, никаких лишних слов):"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')

    async def get_generate_similar(self, expression: str, language: str = "language: RU") -> ServiceResult:
        """
        Генерирует похожее математическое выражение для самостоятельного решения.
        """
        try:
            full_prompt = f"""Создай ОДНУ математическую задачу, похожую на пример.

    Язык: {language}

    ПРАВИЛА (Telegram-friendly):
    - НЕ LaTeX, НЕ Markdown
    - Используй: = + - * / ^ ( ) < > ≤ ≥
    - * для умножения: 5*x
    - ^ для степеней: x^2
    - ТОЛЬКО задача, без решений, без пояснений
    - ОДНА строка

    ПРИМЕРЫ:

    # Уравнения
    Вход: 3*x + 5 = 14
    Выход: 2*x - 4 = 6

    Вход: 7*x = 21
    Выход: 4*x = 16

    Вход: x/2 = 10
    Выход: x/3 = 5

    # Квадратные уравнения
    Вход: x^2 - 9 = 0
    Выход: x^2 - 16 = 0

    Вход: x^2 + 5*x + 6 = 0
    Выход: x^2 + 7*x + 12 = 0

    # Неравенства
    Вход: 2*x + 3 > 7
    Выход: 3*x - 2 < 10

    Вход: x - 5 ≤ 2
    Выход: x + 3 ≥ 8

    Вход: 4*x > 12
    Выход: 5*x < 25

    # Арифметика
    Вход: 25 + 17
    Выход: 32 + 14

    Вход: 15 * 4
    Выход: 12 * 6

    Вход: 100 - 45
    Выход: 80 - 30

    # Дроби
    Вход: 3/4 + 1/2
    Выход: 2/3 + 1/3

    Вход: 5/6 - 1/3
    Выход: 7/8 - 1/4

    # Степени
    Вход: 2^3 + 5
    Выход: 3^2 + 4

    Вход: x^2 + 2*x + 1
    Выход: x^2 + 4*x + 4

    Пример: {expression}

    Похожая задача (только одна строка, без комментариев):"""

            response_text = await self.llm_client.chat_completion(full_prompt)
            return ServiceResult(success=True, data={"response": response_text})
        except Exception:
            return ServiceResult(success=False, message_key='llm_error')