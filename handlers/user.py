from aiogram import types, F, Router
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sympy import Eq, solve, symbols

from keyboards.inline_kbs import page_keyboard
from utils.utils import *
from startup import texts
from states.PlotStates import PlotStates

router = Router()


@router.message(Command("history"))
@router.message(F.text.lower().in_(["история", "history", "История📃"]))
async def user_history(message: types.Message, user_language: str = "RU"):
    rows, next_cursor, prev_cursor = await requests_history(message.from_user.id)

    kb = await page_keyboard(next_cursor, prev_cursor)

    history_text = ""
    for row in rows:
        input_message = row["input_message"].replace(">", "&gt;").replace("<", "&lt;")
        output_message = row["output_message"].replace(">", "&gt;").replace("<", "&lt;")
        history_text += f"• {input_message};\t{texts[user_language]['answer']} <b>{output_message}</b>\n"

    if not history_text:
        history_text = "Пока нет сохранённой истории."

    await message.answer(
        text=f"{texts[user_language]['history_answer']}\n\n{history_text}",
        parse_mode="HTML",
        reply_markup=kb.as_markup() if kb else None
    )


#Решение уравнений
@router.message(F.text.contains("="))
async def solve_equation_or_expression(message: types.Message, user_language: str):
    try:
        print("IN EQUATION")
        # Вводим переменную
        x = symbols('x')

        # Преобразовываем уравнение
        user_input = message.text

        # Разделяем уравнение на левую и правую части
        equation_parts = user_input.split('=')

        # Решаем уравнение и выводим ответ пользователю
        if len(equation_parts) == 2:
            left = equation_parts[0]
            right = equation_parts[1]

            equation = Eq(safe_parse_to_numpy_answer(left), safe_parse_to_numpy_answer(right))

            # Решаем уравнение
            result = solve(equation, x)

            formatted_res = ('; '.join(
                [f'x = {str(round(sol, 3)).rstrip("0").rstrip(".") if "." in str(sol) else str(sol)}' for sol in
                 result]))

            await message.answer(text=formatted_res)
            await save_user_message(message.from_user.id, user_input, formatted_res)
        else: #иначе сообщаем о некорректном вводе
            await message.answer(text=texts[user_language]['wrong_input'])

    except Exception as e: #выводим в сообщение об ошибке
        await message.answer(text=f'{texts[user_language]['error']}{e}')

# Хендлер для неравенств
@router.message(lambda message: any(s in message.text for s in ['<','<=','>=','>']))
async def solve_inequality(message: types.Message, user_language: str):
    try:
        user_input = message.text.lower()

        # Заменяем символы для представления бесконечности
        user_input = user_input.replace('oo', 'sp.oo')

        # Решаем неравенство
        x = sp.symbols('x')
        solution = sp.solve_univariate_inequality(safe_parse_to_numpy_answer(user_input), x, relational=False)

        #в красивую строку
        formatted_solution = f'x ∈ {sp.pretty(solution, use_unicode=True)}'
        await message.answer(text= formatted_solution)
        await save_user_message(message.from_user.id, user_input, formatted_solution)

    except Exception as e: #выводим в сообщение об ошибке
        await message.answer(text=f'{texts[user_language]['error']}{e}')

#Хендлер обработки запросов по состоянию PlotStates.waiting_for_function
@router.message(PlotStates.waiting_for_function)
async def process_plot(message: types.Message, state: FSMContext, user_language: str):
    try:
        text = message.text.strip()
        original_text = text

        # Парсим выражение в безопасную NumPy-функцию
        f_numpy = safe_parse_to_numpy_function(text)
        # Генерируем график
        plot_buf = generate_plot(f_numpy, original_text, user_language)
        raw_bytes = plot_buf.read()
        photo_file = types.BufferedInputFile(raw_bytes, "plot.png")
        # Отправляем результат

        caption_template = texts[user_language]['plot_caption']
        caption_filled = caption_template.format(
            original_text=original_text,
            x_min=x_range[0],
            x_max=x_range[1]
        )
        await message.answer_photo(photo=photo_file, caption=caption_filled, parse_mode='HTML')
        await save_user_message(message.from_user.id, text, 'plot📈')

        await state.clear()
        return None
    except Exception as e:
        # Обработка сообщений об ошибках и запрос на повторный ввод
        await message.answer(text=texts[user_language][f"plot_try_again"])
        print(e)
        return None

# обработчик кнопок листания
@router.callback_query(F.data.startswith("user:history:"))
async def call_handler(callback: CallbackQuery, user_language: str = "RU"):
    parts = callback.data.split(":", 3)
    direction = parts[2]  # "next" или "prev"
    cursor_split = parts[3].split("|", 1)
    cursor = (int(cursor_split[0]), cursor_split[1])  # id + created_at

    rows, next_cursor, prev_cursor = await requests_history(
        callback.from_user.id,
        cursor=cursor,
        direction=direction
    )

    print(f"NEXT: {next_cursor}\nPREV:{prev_cursor}")
    kb = await page_keyboard(next_cursor, prev_cursor)

    history_text = ""
    for row in rows:
        input_message = row["input_message"].replace(">", "&gt;").replace("<", "&lt;")
        output_message = row["output_message"].replace(">", "&gt;").replace("<", "&lt;")
        history_text += f"• {input_message};\t{texts[user_language]['answer']} <b>{output_message}</b>\n"

    if not history_text:
        history_text = "Пока нет сохранённой истории."

    await callback.message.edit_text(
        text=f"{texts[user_language]['history_answer']}\n\n{history_text}",
        parse_mode="HTML",
        reply_markup=kb.as_markup() if kb else None
    )

    await callback.answer()

# Хендлер для остальных сообщений
@router.message()
async def handle_expression(message: types.Message, user_language: str):
    try:
        # Преобразовываем выражение
        user_input = message.text.lower()

        # Решаем выражение
        answer = safe_parse_to_numpy_answer(user_input)
        formatted_res = str(round(answer, 3)).rstrip('0').rstrip('.') if '.' in str(answer) else str(answer)

        await message.answer(text=formatted_res)
        await save_user_message(message.from_user.id, user_input, formatted_res)
    except Exception as e:
        await message.answer(text=f'{texts[user_language]['error']}{e}')