import logging

import aiogram
from aiogram import F, Bot
from aiogram.types import (
    Message,
    LabeledPrice,)
from keyboards.inline_kbs import payment_kb
from services.AccessRights import AccessRights
from Filters.IntentFilter import IntentFilter
from repositories.users_repository import update_subscription_period

router = aiogram.Router()

logger = logging.getLogger(__name__)


# Фукнция для создания ссылки
async def create_stars_invoice_link(
        bot: Bot, description,
        payload, amount, days,
        title: str = "Premium") -> str:
    link = await bot.create_invoice_link(
        title=title,
        description=description,
        payload=payload,
        provider_token='',
        currency='XTR',
        prices=[LabeledPrice(label=f'{title} x {days}', amount=amount)],
    )
    return link

# Ответ на сообщение об успешной оплате
@router.message(F.successful_payment)
async def payment_link_message(message: Message, user_language: str, texts: dict, access_rights: AccessRights):
    payload = message.successful_payment.invoice_payload
    amount = message.successful_payment.total_amount
    charge_id = message.successful_payment.telegram_payment_charge_id

    update_status = await update_subscription_period(message.from_user.id, payload, amount,
                                                     charge_id)  # заносим транзакцию в бд и обновлениям параметры пользователя.
    await access_rights.invalidate_cache(user_id = message.from_user.id) #очищаем кеш
    if update_status:
        await message.answer(texts[user_language]['payments_successful_answer'])
    else:
        await message.answer(texts[user_language]['payments_failed_answer'])

@router.message(IntentFilter("payments"))
async def buy_premium(message: Message, user_language: str, texts: dict):
    # Создаем ссылки для оплаты на разное количество времени
    link1m = await create_stars_invoice_link(message.bot,
                                             description=texts[user_language]['premium_description_for_link'],
                                             payload=f'premium_30_days_{message.from_user.id}', amount=250, days=30,
                                             title=texts[user_language]['premium'])
    link3m = await create_stars_invoice_link(message.bot,
                                             description=texts[user_language]['premium_description_for_link'],
                                             payload=f'premium_90_days_{message.from_user.id}', amount=650, days=90,
                                             title=texts[user_language]['premium'])
    link12m = await create_stars_invoice_link(message.bot,
                                              description=texts[user_language]['premium_description_for_link'],
                                              payload=f'premium_365_days_{message.from_user.id}', amount=2500, days=365,
                                              title=texts[user_language]['premium'])

    await message.answer(text=texts[user_language]['premium_answer'], parse_mode='HTML')
    await message.answer(text=texts[user_language]['premium_choose'],
                         reply_markup=await payment_kb(user_language, link1m = link1m, link3m = link3m, link12m=link12m), parse_mode='HTML')

