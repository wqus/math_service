from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.reply_kbs import kb_info
from keyboards.inline_kbs import kb_language
from services.functions import init_user, update_user_language
from startup import texts
from aiogram.types import CallbackQuery
from states.PlotStates import PlotStates

router = Router()
# HAHDLERS
#choose language and start
@router.message(CommandStart())
@router.message(F.text.lower().in_(["привет", "начать", "hi"]))
async def start_reply(message: types.Message):
    await message.answer(text='Привет!👋\n'
                                           'Пожалуйста выбери язык, на котором тебе будет комфортно общаться:\n\n'
                                           'Hi👋\n'
                                           'Please choose a language:', reply_markup=kb_language)
    await init_user(message.from_user.id, message.from_user.username)

# ответ на умения
@router.message(Command(commands=["skills", "умения"]))
@router.message(F.text.in_([texts['language:RU']['skills'], "умения", texts['language:EN']['skills'], "skills"]))
@router.message(F.text.lower().in_(["умения", "skills", "возможности", "способности"]))
async def skills(message: types.Message, user_language: str):
    await message.answer(text=texts[user_language]['skills_answer'])

#HI message, 2 languages
language_array = ['language:RU', 'language:EN']
@router.callback_query(F.data.startswith("language:"))
async def call_handler(callback: CallbackQuery):
    match callback:
        case _ if callback.data in language_array:
            await callback.message.answer(text=f"{texts[callback.data]['start']}", reply_markup=kb_info[callback.data])
            await update_user_language(callback.from_user.id, callback.data)
            await callback.answer()

# ответ на примечание
@router.message(Command(commands=["rules", "примечание"]))
@router.message(F.text.in_([texts['language:RU']['note'], texts['language:EN']['note']]))
@router.message(F.text.lower().in_(["примечание", "rules", "правила", "note", 'примечание📃', 'notes📃']))
async def primec(message: types.Message, user_language: str):
    await message.answer(text=texts[user_language]['note_answer'], parse_mode='HTML')

# Запрос на график
@router.message(Command(commands=["plot", "график"]))
@router.message(F.text.lower().in_(["график📈", "график", "plot📈", "plot"]))
async def start_plot(message: types.Message, user_language: str, state: FSMContext):
    await message.answer(text=texts[user_language]['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)
