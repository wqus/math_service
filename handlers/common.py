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
    await init_user(message.from_user.id)

#HI message, 2 languages
language_array = ['RU', 'EN']
@router.callback_query()
async def call_handler(callback: CallbackQuery):
    match callback:
        case _ if callback.data in language_array:
            await callback.answer()
            await callback.message.answer(text=f"{texts[callback.data]['start']}", reply_markup=kb_info[callback.data])
            await update_user_language(callback.from_user.id, callback.data)
# ответ на умения
@router.message(Command(commands=["skills", "умения"]))
@router.message(F.text.in_([texts['RU']['skills'], "умения", texts['EN']['skills'], "skills"]))
@router.message(F.text.lower().in_(["умения", "skills", "возможности", "способности"]))
async def skills(message: types.Message, user_language: str):
    match user_language:
        case "EN":
            await message.answer(text= texts['EN']['skills_answer'])
        case "RU":
            await message.answer(text=texts['RU']['skills_answer'])

# ответ на примечание
@router.message(Command(commands=["rules", "примечание"]))
@router.message(F.text.in_([texts['RU']['note'], texts['EN']['note']]))
@router.message(F.text.lower().in_(["примечание", "rules", "правила", "note"]))
async def primec(message: types.Message, user_language: str):
    match user_language:
        case "EN":
            await message.answer(text= texts['EN']['note_answer'], parse_mode='HTML')
        case "RU":
            await message.answer(text=texts['RU']['note_answer'], parse_mode='HTML')

# Запрос на график
@router.message(Command(commands=["plot", "график"]))
@router.message(F.text.lower().in_(["график📈", "график", "plot📈", "plot"]))
async def start_plot(message: types.Message, user_language: str, state: FSMContext):
    match user_language:
        case "EN":
            await message.answer(text=texts['EN']['plot_message'], parse_mode='HTML')
        case "RU":
            await message.answer(text=texts['RU']['plot_message'], parse_mode='HTML')
    await state.set_state(PlotStates.waiting_for_function)
