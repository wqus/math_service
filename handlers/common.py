from aiogram import types, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from Filters.AccessRightsFilter import AccessRightsFilter
from keyboards.reply_kbs import kb_info
from keyboards.inline_kbs import kb_language
from repositories.support_messages_repository import save_message_to_support, save_support_answer_rating
from repositories.users_repository import init_user, update_user_language, check_user_from_db
from aiogram.types import CallbackQuery
from states.PlotStates import PlotStates
from Filters.IntentFilter import IntentFilter
from Filters.HasAttemptsLeftFilter import HasAttemptsLeft
import logging

from states.SupportStates import SupportStates

router = Router()

logger = logging.getLogger(name=__name__)


# HAHDLERS
# choose language and start
@router.message(IntentFilter("start"), CommandStart())
async def start_reply(message: types.Message):
    await message.answer(text='Привет!👋\n'
                              'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                              'Hi👋\n'
                              'Please choose a language:', reply_markup=kb_language)
    await init_user(message.from_user.id)


# ответ на умения
@router.message(AccessRightsFilter(0), IntentFilter("skills"))
async def skills(message: types.Message, user_language: str, texts: dict):
    await message.answer(text=texts[user_language]['skills_answer'])


# HI message, 2 languages
language_array = ['language:RU', 'language:EN']


# Ответ на callback запрос на смену языка
@router.callback_query(AccessRightsFilter(0), F.data.startswith("language:"))
async def call_handler(callback: CallbackQuery, texts: dict):
    match callback:
        case _ if callback.data in language_array:
            await callback.message.answer(text=f"{texts[callback.data]['start']}",
                                          reply_markup=await kb_info(texts, callback.data))
            await update_user_language(callback.from_user.id, callback.data)
            await callback.answer()


# Хендлер для обра оценки тикета
@router.callback_query(AccessRightsFilter(0), F.data.startswith("ticket:"))
async def call_handler(callback: CallbackQuery, texts: dict, bot: Bot, user_language: str):
    splited = callback.data.split(':')
    ticket_id = splited[1]
    rating = splited[2]

    # функция для сохранения в бд оцени по нашему тикет айди
    await save_support_answer_rating(rating, ticket_id)

    # Удаляем клавиатуру под сообщением поддержки после оценки
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)

    await callback.message.answer(text=texts[user_language]['thanks_for_rating'])
    await callback.answer()


# Ответ на примечание
@router.message(AccessRightsFilter(0), IntentFilter("rules"))
async def primec(message: types.Message, user_language: str, texts: dict):
    await message.answer(text=texts[user_language]['note_answer'], parse_mode='HTML')


# Ответ на "Поддержка"
@router.message(AccessRightsFilter(0), IntentFilter("support"))
async def skills(message: types.Message, user_language: str, state: FSMContext, texts: dict):
    await message.answer(text=texts[user_language]['support_write_message'], parse_mode='html')
    await state.set_state(SupportStates.waiting_for_message)


# Обрабатываем запрос пользователя в поддержку
@router.message(SupportStates.waiting_for_message)
async def process_support(message: types.Message, state: FSMContext, user_language: str, texts: dict):
    try:
        ticket_id = await save_message_to_support(message.from_user.id, message.text)
        await message.answer(text=texts[user_language]['support_access'].format(ticket_id=f"SUP-{ticket_id}"),
                             parse_mode='html')
        await state.clear()
    except Exception:
        logger.exception(f"Ошибка при обработке запроса в поддержку, user_id = {message.from_user.id}")
        await message.answer(texts[user_language]['support_error'])


# Запрос на график
@router.message(IntentFilter("plot"), HasAttemptsLeft())
async def start_plot(message: types.Message, user_language: str, state: FSMContext, texts: dict):
    await message.answer(text=texts[user_language]['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)
