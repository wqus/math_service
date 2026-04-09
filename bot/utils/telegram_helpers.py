from aiogram import types, Bot
from aiogram.types import LabeledPrice

from bot.core.ServiceResult import ServiceResult
from bot.presenters.admin_presenter import format_ban_list
from bot.presenters.admin_presenter import format_tickets_list


async def send_tickets(message: types.Message, result: ServiceResult, language: str, texts: dict):
    """
    Отправляет тикеты пользователю.
    """
    if not result.data['tickets']:
        await message.answer(text=texts[language]['support_no_tickets_to_load'])
    else:
        ticket_messages = await format_tickets_list(result.data['tickets'], texts, language)

        for ticket_msg in ticket_messages[:3]:
            await message.answer(text=ticket_msg[0], reply_markup=ticket_msg[1].as_markup(), parse_mode='html')


async def send_bans(message: types.Message, result: ServiceResult, language: str, texts: dict):
    """
    Отправляет список банов пользователю.
    """
    if not result.data['bans']:
        await message.answer(text=texts[language]['no_bans'])
    else:
        bans_messages = await format_ban_list(result.data['bans'], texts, language)

        for ban_msg in bans_messages:
            await message.answer(text=ban_msg[0], reply_markup=ban_msg[1].as_markup(), parse_mode='html')


async def create_stars_invoice_link(
        bot: Bot, description: str,
        payload: str, amount: int, days: int,
        title: str = "Premium") -> str:
    """
    Создает ссылку для оплаты Stars.
    """
    link = await bot.create_invoice_link(
        title=title,
        description=description,
        payload=payload,
        provider_token='',
        currency='XTR',
        prices=[LabeledPrice(label=f'{title} x {days}', amount=amount)],
    )
    return link


