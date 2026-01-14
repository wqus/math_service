from aiogram.filters import BaseFilter
from aiogram import types

class IntentFilter(BaseFilter):
    def __init__(self, intent):
        self.intent = intent
    async def __call__(self, message: types.Message, **kwargs):
        intent_from_data = kwargs.get("intent", "unknown")
        return intent_from_data.value  == self.intent
