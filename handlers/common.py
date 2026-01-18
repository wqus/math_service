from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.reply_kbs import kb_info
from keyboards.inline_kbs import kb_language
from services.functions import init_user, update_user_language, update_subscription_period
from aiogram.types import CallbackQuery
from states.PlotStates import PlotStates
from intents.IntentFilter import IntentFilter
from aiologger import Logger

router = Router()

logger = Logger(name = __name__)

# HAHDLERS
#choose language and start
@router.message(CommandStart())
@router.message(IntentFilter("start"))
async def start_reply(message: types.Message):
    await message.answer(text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
    await init_user(message.from_user.id, message.from_user.username)

# ответ на умения
@router.message(IntentFilter("skills"))
async def skills(message: types.Message, user_language: str, texts: dict):
    await message.answer(text=texts[user_language]['skills_answer'])

#HI message, 2 languages
language_array = ['language:RU', 'language:EN']
@router.callback_query(F.data.startswith("language:"))
async def call_handler(callback: CallbackQuery, texts: dict):
    match callback:
        case _ if callback.data in language_array:
            await callback.message.answer(text=f"{texts[callback.data]['start']}", reply_markup= await kb_info(texts, callback.data))
            await update_user_language(callback.from_user.id, callback.data)
            await callback.answer()

# ответ на примечание
@router.message(IntentFilter("rules"))
async def primec(message: types.Message, user_language: str, texts: dict):
    await message.answer(text=texts[user_language]['note_answer'], parse_mode='HTML')

# Запрос на график
@router.message(IntentFilter("plot"))
async def start_plot(message: types.Message, user_language: str, state: FSMContext, texts: dict):
    await message.answer(text=texts[user_language]['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)



