from aiogram import types
import logging


async def kb_info(texts, language):
    logger = logging.getLogger(__name__)
    logger.debug("Создание reply keyboard")
    '''
    kb = {
        'language:RU': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=texts['language:RU']['skills']),
                                                            types.KeyboardButton(text=texts['language:RU']['note'])],
                                                           [types.KeyboardButton(text=texts['language:RU']['plot']),
                                                            types.KeyboardButton(text=texts['language:RU']['history'])],
                                                           [types.KeyboardButton(text = texts['language:RU']['premium'])]],
                                                 resize_keyboard=True),
        'language:EN': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=texts['language:EN']['skills']),
                                                            types.KeyboardButton(text=texts['language:EN']['note'])],
                                                           [types.KeyboardButton(text=texts['language:EN']['plot']),
                                                            types.KeyboardButton(text=texts['language:EN']['history'])],
                                                           [types.KeyboardButton(text = texts['language:EN']['premium'])]],
                                                 resize_keyboard=True)
    }
    '''
    kb = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=texts[language]['skills']),
                                              types.KeyboardButton(text=texts[language]['note'])],
                                             [types.KeyboardButton(text=texts[language]['support']),
                                              types.KeyboardButton(text=texts[language]['history'])],
                                             [types.KeyboardButton(text=texts[language]['plot'])],
                                             [types.KeyboardButton(text=texts[language]['premium'])]],
                                   resize_keyboard=True)
    return kb
