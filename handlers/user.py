from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from sympy import Eq, solve, symbols
from utils.utils import *
from startup import texts
from states.PlotStates import PlotStates

router = Router()
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
        formatted_solution = sp.pretty(solution, use_unicode=True)
        await message.answer(text=f'x ∈ {formatted_solution}')

    except Exception as e: #выводим в сообщение об ошибке
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')

#Решение уравнений
@router.message(F.text.contains("="))
async def solve_equation_or_expression(message: types.Message, user_language: str):
    try:
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
            match user_language: #отправляем ответ
                case "EN":
                    await message.answer(text=formatted_res)
                case "RU":
                    await message.answer(text=formatted_res)
        else: #иначе сообщаем о некорректном вводе
            match user_language:
                case "EN":
                    await message.answer(text=texts['EN']['wrong_input'])
                case "RU":
                    await message.answer(text=texts['RU']['wrong_input'])

    except Exception as e: #выводим в сообщение об ошибке
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')

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
        match user_language:
            case "EN":
                caption_template = texts['EN']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                await message.answer_photo(photo = photo_file, caption=caption_filled, parse_mode='HTML')
            case "RU":
                caption_template = texts['RU']['plot_caption']
                caption_filled = caption_template.format(
                    original_text=original_text,
                    x_min=x_range[0],
                    x_max=x_range[1]
                )
                await message.answer_photo(photo = photo_file, caption=caption_filled, parse_mode='HTML')
        await state.clear()
        return None
    except Exception as e:
        # Обработка сообщений об ошибках и запрос на повторный ввод
        error_msg = str(e)
        match user_language:
            case "EN":
                await message.answer(text=f"Error: {error_msg}")
                await message.answer(text=texts["EN"][f"plot_try_again"])
            case "RU":
                await message.answer(text=f"Ошибка: {error_msg}")
                await message.answer(text=texts["RU"][f"plot_try_again"])
        print(e)
        return None

# Хендлер для остальных сообщений
@router.message()
async def handle_expression(message: types.Message, user_language: str):
    try:
        # Преобразовываем выражение
        user_input = message.text.lower()

        # Решаем выражение
        answer = safe_parse_to_numpy_answer(user_input)

        formatted_res = str(round(answer, 3)).rstrip('0').rstrip('.') if '.' in str(answer) else str(answer)
        match user_language:  # отправляем ответ
            case "EN":
                await message.answer(text=formatted_res)
            case "RU":
                await message.answer(text=formatted_res)

    except Exception as e:
        match user_language:
            case "EN":
                await message.answer(text=f'{texts['EN']['error']}{e}')
            case "RU":
                await message.answer(text=f'{texts['RU']['error']}{e}')
