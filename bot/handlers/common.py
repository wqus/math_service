from aiogram import types, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.Filters.AccessRightsFilter import AccessRightsFilter
from bot.keyboards.reply_kbs import kb_info
from bot.keyboards.inline_kbs import kb_language
from aiogram.types import CallbackQuery

from bot.services.AdminService import AdminService
from bot.services.UserService import UserService
from bot.states.PlotStates import PlotStates
from bot.Filters.IntentFilter import IntentFilter
from bot.Filters.HasAttemptsLeftFilter import HasAttemptsLeft
import logging

from bot.states.SupportStates import SupportStates

router = Router()

logger = logging.getLogger(name=__name__)

language_array = ['language:RU', 'language:EN']

@router.message(CommandStart())
@router.message(IntentFilter("start"))
async def handle_start(message: types.Message, user_service: UserService):
    """
    Обрабатывает команду /start и инициализирует пользователя.
    """
    await message.answer(text='Привет!👋\n'
                              'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                              'Hi👋\n'
                              'Please choose a language:', reply_markup=kb_language)
    await user_service.init_user(message.from_user.id)


@router.message(AccessRightsFilter(0), IntentFilter("skills"))
async def show_skills(message: types.Message, user_language: str, texts: dict):
    """
    Показывает информацию о навыках бота.
    """
    await message.answer(text=texts[user_language]['skills_answer'])


@router.callback_query(AccessRightsFilter(0), F.data.startswith("language:"))
async def handle_language_selection(callback: CallbackQuery, texts: dict, user_service: UserService):
    """
    Обрабатывает выбор языка пользователем.
    """
    match callback:
        case _ if callback.data in language_array:
            update_language_res = await user_service.update_user_language(callback.from_user.id, callback.data)

            if update_language_res:
                message_key = 'start'
            else:
                message_key = 'update_language_error'
            await callback.message.answer(text=f"{texts[callback.data][message_key]}",
                                          reply_markup=await kb_info(texts, callback.data))
            await callback.answer()


@router.message(AccessRightsFilter(0), IntentFilter("rules"))
async def show_rules(message: types.Message, user_language: str, texts: dict):
    """
    Показывает правила использования бота.
    """
    await message.answer(text=texts[user_language]['note_answer'], parse_mode='HTML')


@router.message(AccessRightsFilter(0), IntentFilter("support"))
async def start_support_request(message: types.Message, user_language: str, state: FSMContext, texts: dict):
    """
    Начинает процесс создания запроса в поддержку.
    """
    await message.answer(text=texts[user_language]['support_write_message'], parse_mode='html')
    await state.set_state(SupportStates.waiting_for_message)


@router.message(SupportStates.waiting_for_message)
async def process_support_request(message: types.Message, state: FSMContext, user_language: str, texts: dict,
                                  admin_service: AdminService):
    """
    Обрабатывает запрос пользователя в поддержку.
    """
    try:
        result = await admin_service.create_support_message(message.from_user.id, message.text)

        if result.success:
            ticket_id = result.data.get('ticket_id')
            await message.answer(
                text=texts[user_language]['support_access'].format(ticket_id=f"SUP-{ticket_id}"),
                parse_mode='html'
            )
            await state.clear()
        else:
            await message.answer(texts[user_language]['support_error'])

    except Exception:
        logger.exception(f"Ошибка при обработке запроса в поддержку, user_id = {message.from_user.id}")
        await message.answer(texts[user_language]['support_error'])


@router.message(IntentFilter("plot"), HasAttemptsLeft())
async def start_plot_generation(message: types.Message, user_language: str, state: FSMContext, texts: dict):
    """
    Начинает процесс генерации графика.
    """
    await message.answer(text=texts[user_language]['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)