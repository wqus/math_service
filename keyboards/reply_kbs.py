from aiogram import types


async def kb_info(texts, language):
    kb = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=texts[language]['skills']),
                                              types.KeyboardButton(text=texts[language]['note'])],
                                             [types.KeyboardButton(text=texts[language]['support']),
                                              types.KeyboardButton(text=texts[language]['history'])],
                                             [types.KeyboardButton(text=texts[language]['plot'])],
                                             [types.KeyboardButton(text=texts[language]['premium'])]],
                                   resize_keyboard=True)
    return kb
