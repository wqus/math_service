import logging

import aiogram
from aiogram import F
from aiogram.types import Message
from keyboards.inline_kbs import payment_kb
from services.AccessService import AccessService
from Filters.IntentFilter import IntentFilter

from services.PaymentsService import PaymentsService
from utils.telegram_helpers import create_stars_invoice_link

router = aiogram.Router()

logger = logging.getLogger(__name__)


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, user_language: str, texts: dict, access_rights: AccessService,
                                     payments_service: PaymentsService):
    """
    Обрабатывает успешную оплату и обновляет подписку пользователя.
    """
    payload = message.successful_payment.invoice_payload
    amount = message.successful_payment.total_amount
    charge_id = message.successful_payment.telegram_payment_charge_id

    update_result = await payments_service.update_subscription_period(
        message.from_user.id, payload, amount, charge_id
    )
    await access_rights.invalidate_access_cache(user_id=message.from_user.id)

    if update_result.success:
        await message.answer(texts[user_language][update_result.message_key])


@router.message(IntentFilter("payments"))
async def show_premium_options(message: Message, user_language: str, texts: dict):
    """
    Показывает варианты покупки Premium подписки.
    """
    link1m = await create_stars_invoice_link(
        message.bot,
        description=texts[user_language]['premium_description_for_link'],
        payload=f'premium_30_days_{message.from_user.id}',
        amount=250,
        days=30,
        title=texts[user_language]['premium']
    )
    link3m = await create_stars_invoice_link(
        message.bot,
        description=texts[user_language]['premium_description_for_link'],
        payload=f'premium_90_days_{message.from_user.id}',
        amount=650,
        days=90,
        title=texts[user_language]['premium']
    )
    link12m = await create_stars_invoice_link(
        message.bot,
        description=texts[user_language]['premium_description_for_link'],
        payload=f'premium_365_days_{message.from_user.id}',
        amount=2500,
        days=365,
        title=texts[user_language]['premium']
    )

    await message.answer(text=texts[user_language]['premium_answer'], parse_mode='HTML')
    await message.answer(
        text=texts[user_language]['premium_choose'],
        reply_markup=await payment_kb(user_language, link1m=link1m, link3m=link3m, link12m=link12m),
        parse_mode='HTML'
    )