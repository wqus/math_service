from aiogram import types, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sympy import Eq, solve, symbols
import datetime as dt

from bot.Filters.AccessRightsFilter import AccessRightsFilter
from bot.Filters.IntentFilter import IntentFilter
from bot.keyboards.reply_kbs import kb_info
from bot.presenters.history_presenter import format_history_list
from bot.services.AccessService import AccessService
from bot.services.HistoryService import HistoryService
from bot.services.AIService import AIService
from bot.utils.utils import *
from bot.states.PlotStates import PlotStates
from keyboards.inline_kbs import ai_functions_kb

router = Router()


@router.message(AccessRightsFilter(0), IntentFilter("history"))
async def show_user_history(message: types.Message, texts: dict, history_service: HistoryService,
                            user_language: str = "RU"):
    """
    Показывает историю сообщений пользователя.
    """
    result = await history_service.get_user_history(message.from_user.id)

    if result.success:
        formatted_history_text, pagination_kb = await format_history_list(
            result.data['rows'],
            result.data['next_cursor'],
            result.data['prev_cursor'],
            texts,
            language=user_language
        )
        await message.answer(
            text=formatted_history_text,
            parse_mode="HTML",
            reply_markup=pagination_kb.as_markup() if pagination_kb else None
        )
    else:
        await message.answer(
            text=texts[user_language]['history_error'],
            parse_mode="HTML")


@router.message(AccessRightsFilter(0), F.text.contains("="))
async def solve_equation(message: types.Message, user_language: str, texts: dict, history_service: HistoryService):
    """
    Решает математическое уравнение.
    """
    try:
        x = symbols('x')
        user_input = message.text
        equation_parts = user_input.split('=')

        if len(equation_parts) == 2:
            left = equation_parts[0]
            right = equation_parts[1]

            equation = Eq(safe_parse_to_numpy_answer(left), safe_parse_to_numpy_answer(right))
            solutions = solve(equation, x)

            formatted_solutions = ('; '.join(
                [f'x = {str(round(sol, 3)).rstrip("0").rstrip(".") if "." in str(sol) else str(sol)}' for sol in
                 solutions]))
            keyboard = await ai_functions_kb(user_input, texts[user_language]['show_solution'],
                                             texts[user_language]['generate_similar'])
            await message.answer(text=formatted_solutions, reply_markup=keyboard.as_markup())
            await history_service.save_message(message.from_user.id, user_input, formatted_solutions)
        else:
            await message.answer(text=texts[user_language]['wrong_input'])

    except Exception as e:
        await message.answer(text=f'{texts[user_language]["error"]}{e}')


@router.message(AccessRightsFilter(0), lambda message: any(s in message.text for s in ['<', '<=', '>=', '>']))
async def solve_inequality(message: types.Message, user_language: str, texts: dict, history_service: HistoryService):
    """
    Решает математическое неравенство.
    """
    try:
        user_input = message.text.lower()
        user_input = user_input.replace('oo', 'sp.oo')

        x = sp.symbols('x')
        solution = sp.solve_univariate_inequality(safe_parse_to_numpy_answer(user_input), x, relational=False)

        formatted_solution = f'x ∈ {sp.pretty(solution, use_unicode=True)}'
        keyboard = await ai_functions_kb(user_input, texts[user_language]['show_solution'],
                                         texts[user_language]['generate_similar'])
        await message.answer(text=formatted_solution, reply_markup=keyboard.as_markup())
        await history_service.save_message(message.from_user.id, user_input, formatted_solution)

    except Exception as e:
        await message.answer(text=f'{texts[user_language]["error"]}{e}')


@router.message(PlotStates.waiting_for_function)
async def generate_and_send_plot(
        message: types.Message,
        state: FSMContext,
        user_language: str,
        texts: dict,
        access_service: AccessService,
        history_service: HistoryService
):
    """
    Генерирует и отправляет график функции.
    """
    try:
        original_text = message.text.strip()
        f_numpy = safe_parse_to_numpy_function(original_text)
        plot_buf = generate_plot(f_numpy, original_text, user_language)

        raw_bytes = plot_buf.read()

        x_range = (-10, 10)
        caption_template = texts[user_language]['plot_caption']
        caption_filled = caption_template.format(
            original_text=original_text,
            x_min=x_range[0],
            x_max=x_range[1]
        )

        await history_service.save_message(message.from_user.id, original_text, 'plot📈')

        reply_markup = await kb_info(texts, user_language)

        await message.answer_photo(
            photo=types.BufferedInputFile(raw_bytes, filename="plot.png"),
            caption=caption_filled,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        await state.clear()
        attempts_left = await access_service.decrease_attempts(message.from_user.id)

        if attempts_left <= 0:
            await message.answer(texts[user_language]['attempts_ended'], parse_mode='HTML')

    except Exception as e:
        await message.answer(texts[user_language]["plot_try_again"])
        await state.clear()


@router.callback_query(AccessRightsFilter(0), F.data.startswith("ai:"))
async def ai_functions(callback: CallbackQuery, ai_service: AIService, texts: dict = 'RU', user_language: str = 'RU'):
    """
    Обрабатывает callback-запросы для AI функций (решение и генерация).
    """
    split_data = callback.data.split(":")
    function_type = split_data[1]
    user_input = split_data[2]

    if function_type == 'show_solution':
        solution_result = await ai_service.get_show_solution(user_input, user_language)
        answer = texts[user_language]['send_similar'].format(expression = user_input, similar = solution_result.data['response'])
        await callback.message.answer(text=answer)
    elif function_type == 'generate_similar':
        similar_result = await ai_service.get_generate_similar(user_input, user_language)
        answer = texts[user_language]['send_similar'].format(expression = user_input, similar = similar_result.data['response'])
        await callback.message.answer(text=answer)

@router.callback_query(AccessRightsFilter(0), F.data.startswith("user:history:"))
async def paginate_history(callback: CallbackQuery, texts: dict, history_service: HistoryService,
                           user_language: str = "RU"):
    """
    Обрабатывает пагинацию истории сообщений.
    """
    parts = callback.data.split(":", 3)
    direction = parts[2]
    cursor_split = parts[3].split("|", 1)
    cursor = (int(cursor_split[0]), dt.datetime.fromisoformat(cursor_split[1]))

    result = await history_service.get_user_history(
        callback.from_user.id,
        cursor=cursor,
        direction=direction
    )

    formatted_history_text, pagination_kb = await format_history_list(
        result.data['rows'],
        result.data['next_cursor'],
        result.data['prev_cursor'],
        texts,
        language=user_language
    )

    await callback.message.edit_text(
        text=formatted_history_text,
        parse_mode="HTML",
        reply_markup=pagination_kb.as_markup() if pagination_kb else None
    )
    await callback.answer()


@router.message(AccessRightsFilter(0), IntentFilter("unknown"))
async def evaluate_expression(message: types.Message, user_language: str, texts: dict, history_service: HistoryService):
    """
    Вычисляет математическое выражение.
    """
    try:
        user_input = message.text.lower()

        answer = safe_parse_to_numpy_answer(user_input)
        formatted_result = str(round(answer, 3)).rstrip('0').rstrip('.') if '.' in str(answer) else str(answer)
        keyboard = await ai_functions_kb(user_input, texts[user_language]['show_solution'],
                                         texts[user_language]['generate_similar'])
        await message.answer(text=formatted_result, reply_markup=keyboard.as_markup())
        await history_service.save_message(message.from_user.id, user_input, formatted_result)
    except Exception as e:
        await message.answer(text=f'{texts[user_language]["error"]}{e}')
