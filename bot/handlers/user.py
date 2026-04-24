from aiogram import types, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import datetime as dt

from bot.Filters.AccessRightsFilter import AccessRightsFilter
from bot.Filters.IntentFilter import IntentFilter

from bot.keyboards.reply_kbs import kb_info
from bot.keyboards.inline_kbs import ai_functions_kb

from bot.presenters.history_presenter import format_history_list

from bot.services.AccessService import AccessService
from bot.services.HistoryService import HistoryService
from bot.services.AIService import AIService

from bot.states.PlotStates import PlotStates

from bot.utils.utils import (
    solve_equation,
    solve_inequality,
    evaluate_expression,
    to_numpy_function,
    generate_plot
)
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
async def handle_equation(message: types.Message, user_language: str, texts: dict,
                          history_service: HistoryService):

    try:
        result = solve_equation(message.text)

        keyboard = await ai_functions_kb(
            message.text,
            texts[user_language]['show_solution'],
            texts[user_language]['generate_similar']
        )

        await message.answer(result, reply_markup=keyboard.as_markup())

        await history_service.save_message(
            message.from_user.id,
            message.text,
            result
        )

    except Exception as e:
        await message.answer(f"{texts[user_language]['error']}{e}")


@router.message(AccessRightsFilter(0), lambda m: any(op in m.text for op in ['<', '>', '<=', '>=']))
async def handle_inequality(message: types.Message, user_language: str, texts: dict,
                            history_service: HistoryService):

    try:
        result = solve_inequality(message.text)

        keyboard = await ai_functions_kb(
            message.text,
            texts[user_language]['show_solution'],
            texts[user_language]['generate_similar']
        )

        await message.answer(result, reply_markup=keyboard.as_markup())

        await history_service.save_message(
            message.from_user.id,
            message.text,
            result
        )

    except Exception as e:
        await message.answer(f"{texts[user_language]['error']}{e}")


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
        expr = message.text.strip()

        f = to_numpy_function(expr)
        buf = generate_plot(f, expr, user_language)

        await history_service.save_message(
            message.from_user.id,
            expr,
            "plot📈"
        )

        await message.answer_photo(
            photo=types.BufferedInputFile(buf.read(), filename="plot.png"),
            caption=texts[user_language]['plot_caption'].format(expr),
            parse_mode="HTML",
            reply_markup=await kb_info(texts, user_language)
        )

        await state.clear()

        left = await access_service.decrease_attempts(message.from_user.id)

        if left <= 0:
            await message.answer(texts[user_language]['attempts_ended'])

    except Exception as e:
        await message.answer(texts[user_language]["plot_try_again"])
        await state.clear()


@router.callback_query(AccessRightsFilter(0), F.data.startswith("ai:"))
async def ai_functions(callback: CallbackQuery, ai_service: AIService, texts: dict = 'RU', user_language: str = 'RU'):
    """
    Обрабатывает запросы для AI функций (решение и генерация).
    """
    split_data = callback.data.split(":")
    function_type = split_data[1]
    user_input = split_data[2]

    if function_type == 'show_solution':
        solution_result = await ai_service.get_show_solution(user_input, user_language)

        if solution_result.success and solution_result.data and solution_result.data.get('response'):
            solution_text = solution_result.data['response'].strip()
            if solution_text:
                answer = texts[user_language]['send_solution'].format(
                    expression=user_input,
                    solution=solution_text)
            else:
                answer = texts[user_language]['no_solution'].format(expression=user_input)
        else:
            answer = texts[user_language]['solution_error'].format(expression=user_input)

        await callback.message.answer(text=answer)

    elif function_type == 'generate_similar':
        similar_result = await ai_service.get_generate_similar(user_input, user_language)

        if similar_result.success and similar_result.data and similar_result.data.get('response'):
            similar_text = similar_result.data['response'].strip()
            if similar_text:
                answer = texts[user_language]['send_similar'].format(
                    expression=user_input,
                    similar=similar_text
                )
            else:
                answer = texts[user_language]['no_similar'].format(expression=user_input)
        else:
            answer = texts[user_language]['generation_error'].format(expression=user_input)

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
async def handle_expression(message: types.Message, user_language: str, texts: dict,
                            history_service: HistoryService):

    try:
        result = evaluate_expression(message.text)

        keyboard = await ai_functions_kb(
            message.text,
            texts[user_language]['show_solution'],
            texts[user_language]['generate_similar']
        )

        await message.answer(result, reply_markup=keyboard.as_markup())

        await history_service.save_message(
            message.from_user.id,
            message.text,
            result
        )

    except Exception as e:
        await message.answer(f"{texts[user_language]['error']}{e}")