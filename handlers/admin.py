from aiogram import Router
from aiogram import Bot
from Filters.AccessRightsFilter import AccessRightsFilter
from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.reply_kbs import kb_info
from keyboards.inline_kbs import kb_language, answer_to_ticket_kb, load_three_tickets_kb, rate_support_answer_kb
from repositories.support_messages_repository import save_message_to_support, take_tickets_for_support, \
    save_support_answer_to_db
from repositories.users_repository import init_user, update_user_language
from aiogram.types import CallbackQuery
from states.PlotStates import PlotStates
from Filters.IntentFilter import IntentFilter
from Filters.HasAttemptsLeftFilter import HasAttemptsLeft
import logging

from states.SupportStates import SupportStates
from utils.utils import show_tickets

router = Router()
router.message.filter(AccessRightsFilter(min_level=2))
router.callback_query.filter(AccessRightsFilter(min_level=2))

logger = logging.getLogger(name=__name__)


# Хендлер, чтобы выводить заявки пользователей(по 3 штуки)
@router.message(AccessRightsFilter(2), Command("tickets"))
async def ticket_command(message: types.Message, user_language: str, texts: dict):
    tickets, last_3_tickets, has_more = await show_tickets(texts, user_language)
    for msg, kb in tickets:
        await message.answer(text=msg, reply_markup=kb.as_markup())

    if has_more:
        kb_ask_for_more = await load_three_tickets_kb(last_3_tickets[-1]['id'],
                                                      "✅")
        await message.answer(text=texts[user_language]['support_load_more'],
                             reply_markup=kb_ask_for_more.as_markup())
    else:
        await message.answer(text=texts[user_language]['support_no_tickets_to_load'])


# Хендлер для обработна нажатий на inline кнопки от админов
@router.callback_query(F.data.startswith("admin"))
async def call_handler(callback: CallbackQuery, state: FSMContext, user_language: str, texts: dict):
    splited = callback.data.split(':')
    match splited[1]:
        case 'answer':
            ticket_id = splited[2]
            ticket_user_id = splited[3]
            # Устанавливаем state = 'waiting_for_ticket_answer'
            await callback.message.answer(text=texts[user_language]['support_ask_for_answer'])
            await state.update_data(ticket_chat_id=callback.message.chat.id)
            await state.update_data(ticket_message_id=callback.message.message_id)
            await state.update_data(ticket_id=ticket_id)
            await state.update_data(ticket_user_id=ticket_user_id)
            await state.set_state(SupportStates.waiting_for_answer)
        case 'load':
            # Вызов функции для загрузки ещё тикетов
            current_position = int(splited[2])
            tickets, last_3_tickets, has_more = await show_tickets(texts=texts, language=user_language,
                                                                   current_position=current_position)
            for msg, kb in tickets:
                await callback.message.answer(text=msg, reply_markup=kb.as_markup())

            if has_more:
                kb_ask_for_more = await load_three_tickets_kb(last_3_tickets[-1]['id'],
                                                              "✅")
                await callback.message.answer(text=texts[user_language]['support_load_more'],
                                              reply_markup=kb_ask_for_more.as_markup())
            else:
                await callback.message.answer(text=texts[user_language]['support_no_tickets_to_load'])
    await callback.answer()


# Хендлер для ответа на тикеты
@router.message(SupportStates.waiting_for_answer)
async def process_answer_to_ticket(message: types.Message, state: FSMContext, user_language: str, texts: dict,
                                   bot: Bot):
    try:
        data = await state.get_data()
        ticket_chat_id = data.get('ticket_chat_id')
        ticket_message_id = data.get('ticket_message_id')
        ticket_id = data.get('ticket_id')
        ticket_user_id = data.get('ticket_user_id')
        await save_support_answer_to_db(ticket_id, message.text, message.from_user.id)  # обновляем тикет в бд
        await message.answer(
            text=texts[user_language]['support_success_answer'])  # Отправляем сообщение об успешной отправке
        await state.clear()
        text_for_user = texts[user_language]['text_for_user'].format(ticket_id=ticket_id, answer_message=message.text)

        # Отправляем сообщение пользователю
        rating_kb = await rate_support_answer_kb(ticket_id)
        await bot.send_message(chat_id=ticket_user_id, text=text_for_user,
                               reply_markup=rating_kb.as_markup(), parse_mode='HTML')

        await bot.edit_message_reply_markup(chat_id=ticket_chat_id, message_id=ticket_message_id,
                                            reply_markup=None)  # Убираем в списке тикетов кнопку "ответить" под текущим
    except Exception:
        await message.answer(text=texts[user_language]['support_failed_answer'])
        await state.clear()
