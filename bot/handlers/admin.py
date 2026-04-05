from aiogram import Bot
from Filters.AccessRightsFilter import AccessRightsFilter
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline_kbs import rate_support_answer_kb, load_three_bans_kb
from aiogram.types import CallbackQuery

from services.AccessService import AccessService
from services.AdminService import AdminService
from utils.telegram_helpers import send_bans, send_tickets

from states.SupportStates import SupportStates

router = Router()
router.message.filter(AccessRightsFilter(min_level=2))
router.callback_query.filter(AccessRightsFilter(min_level=2))


@router.message(Command("tickets"))
async def handle_tickets_command(message: types.Message, user_language: str, texts: dict,
                                 admin_service: AdminService):
    """
    Обрабатывает команду /tickets для вывода списка тикетов.
    """
    fetch_tickets_result = await admin_service.fetch_tickets()

    if fetch_tickets_result.success:
        await send_tickets(message, fetch_tickets_result, user_language, texts)
        has_more_kb = load_three_bans_kb(fetch_tickets_result.data['last_ticket_id'], "✅") if fetch_tickets_result.data[
            'has_more'] else None
        await message.answer(text=texts[user_language][fetch_tickets_result.message_key], reply_markup=has_more_kb)
    else:
        await message.answer(text=texts[user_language][fetch_tickets_result.message_key])


@router.message(SupportStates.waiting_for_answer)
async def process_ticket_answer(message: types.Message, state: FSMContext, user_language: str, texts: dict,
                                bot: Bot, admin_service: AdminService):
    """
    Обрабатывает ответ администратора на тикет.
    """
    try:
        data = await state.get_data()
        ticket_message_id = data.get('ticket_message_id')
        ticket_id = int(data.get('ticket_id'))
        ticket_user_id = data.get('ticket_user_id')

        result = await admin_service.save_support_answer(ticket_id, message.text, message.from_user.id)
        if result.success:
            rating_kb = await rate_support_answer_kb(ticket_id)
            await bot.send_message(chat_id=ticket_user_id, text=message.text,
                                   reply_markup=rating_kb.as_markup(), parse_mode='HTML')

            await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=ticket_message_id,
                                                reply_markup=None)

            await message.answer(
                text=texts[user_language][result.message_key])
        else:
            await message.answer(text=texts[user_language][result.message_key])
        await state.clear()
    except Exception:
        await message.answer(text=texts[user_language]['support_failed_answer'])
        await state.clear()


@router.callback_query(F.data.startswith("admin"))
async def handle_ticket_admin_callback(callback: CallbackQuery, state: FSMContext, user_language: str, texts: dict,
                                       admin_service: AdminService):
    """
    Обрабатывает callback-запросы для тикетов (ответ и загрузка).
    """
    split_data = callback.data.split(':')
    match split_data[1]:
        case 'answer':
            ticket_id = split_data[2]
            ticket_user_id = split_data[3]
            await callback.message.answer(text=texts[user_language]['support_ask_for_answer'])
            await state.update_data(ticket_message_id=callback.message.message_id)
            await state.update_data(ticket_id=ticket_id)
            await state.update_data(ticket_user_id=ticket_user_id)
            await state.set_state(SupportStates.waiting_for_answer)
        case 'load':
            current_position = int(split_data[2])
            fetch_tickets_result = await admin_service.fetch_tickets(current_position=current_position)

            if fetch_tickets_result.success:
                await send_bans(callback.message, fetch_tickets_result, user_language, texts)
                has_more_kb = load_three_bans_kb(fetch_tickets_result.data['last_ticket_id'], "✅") if \
                fetch_tickets_result.data[
                    'has_more'] else None
                await callback.message.answer(text=texts[user_language][fetch_tickets_result.message_key],
                                              reply_markup=has_more_kb)
            else:
                await callback.message.answer(text=texts[user_language][fetch_tickets_result.message_key])
    await callback.answer()


@router.message(AccessRightsFilter(3), Command("add_admin"))
async def handle_add_admin_command(message: types.Message, user_language: str, texts: dict,
                                   access_service: AccessService):
    """
    Обрабатывает команду /add_admin для назначения администратора.
    """
    args = message.text.split(maxsplit=2)
    if len(args) != 2:
        await message.answer(text=texts[user_language]['right_add_admin_usage'])
        return

    user_id = int(args[1])

    assign_admin_result = await access_service.assign_admin(user_id)
    if assign_admin_result.success:
        await message.answer(text=texts[user_language][assign_admin_result.message_key].format(user_id=user_id))


@router.message(AccessRightsFilter(3), Command("remove_admin"))
async def handle_remove_admin_command(message: types.Message, user_language: str, texts: dict,
                                      access_service: AccessService):
    """
    Обрабатывает команду /remove_admin для удаления администратора.
    """
    args = message.text.split(maxsplit=2)
    if len(args) != 2:
        await message.answer(text=texts[user_language]['right_remove_admin_usage'])
        return

    user_id = int(args[1])

    remove_admin_result = await access_service.remove_admin(user_id)
    if remove_admin_result:
        await message.answer(text=texts[user_language][remove_admin_result.message_key].format(user_id=user_id))


@router.message(Command("ban"))
async def handle_ban_user_command(message: types.Message, user_language: str, texts: dict, access_service: AccessService):
    """
    Обрабатывает команду /ban для блокировки пользователя.
    """
    args = message.text.split(maxsplit=2)
    if len(args) != 3:
        await message.answer(text=texts[user_language]['right_ban_usage'])
        return

    user_id = int(args[1])
    reason = args[2]
    ban_user_result = await access_service.ban_user(user_id, message.from_user.id, reason)
    if ban_user_result.success:
        await message.answer(text=texts[user_language][ban_user_result.message_key].format(user_id=user_id))


@router.message(Command("bans_history"))
async def handle_bans_history_command(message: types.Message, user_language: str, texts: dict, admin_service: AdminService):
    """
    Обрабатывает команду /bans_history для вывода истории банов.
    """
    fetch_bans_result = await admin_service.fetch_bans()
    if fetch_bans_result.success:
        await send_bans(message, fetch_bans_result, user_language, texts)
        if fetch_bans_result.data['bans']:
            has_more_kb = load_three_bans_kb(fetch_bans_result.data['last_ban_id'], "✅") if fetch_bans_result.data[
                'has_more'] else None
            await message.answer(text=texts[user_language][fetch_bans_result.message_key], reply_markup=has_more_kb)
    else:
        await message.answer(text=texts[user_language][fetch_bans_result.message_key])


@router.callback_query(F.data.startswith("unban"))
async def handle_unban_user_callback(callback: CallbackQuery, user_language: str, texts: dict, bot: Bot,
                                     access_service: AccessService):
    """
    Обрабатывает callback-запрос для разблокировки пользователя.
    """
    user_id = int(callback.data.split(':')[1])

    unban_result = await access_service.unban_user(user_id)
    if unban_result.success:
        await callback.message.answer(text=texts[user_language][unban_result.message_key].format(user_id=user_id))
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=None)
    else:
        await callback.message.answer(text=texts[user_language][unban_result.message_key])
    await callback.answer()


@router.callback_query(F.data.startswith("bans"))
async def handle_load_bans_callback(callback: CallbackQuery, user_language: str, texts: dict, admin_service: AdminService):
    """
    Обрабатывает callback-запрос для дозагрузки списка банов.
    """
    last_ban_id = int(callback.data.split(':')[2])
    fetch_bans_result = await admin_service.fetch_bans(current_position=last_ban_id)

    if fetch_bans_result.success:
        await send_bans(callback.message, fetch_bans_result, user_language, texts)
        has_more_kb = load_three_bans_kb(fetch_bans_result.data['last_ban_id'], "✅") if fetch_bans_result.data[
            'has_more'] else None
        await callback.message.answer(text=texts[user_language][fetch_bans_result.message_key], reply_markup=has_more_kb)
    else:
        await callback.message.answer(text=texts[user_language][fetch_bans_result.message_key])
    await callback.answer()