from aiogram import BaseMiddleware
from bot.intents.intent_detect import detect_intent

class IntentMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        text = event.text if hasattr(event, 'text') else ''
        lang = data.get('user_language', 'language:RU')

        data['intent'] = detect_intent(text, lang)
        return await handler(event, data)
