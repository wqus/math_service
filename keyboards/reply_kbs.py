from aiogram import types
from startup import texts
# KEY BOARDS
#REPLY_KBs
kb_info = {
    'language:RU': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['language:RU']['skills']), types.KeyboardButton(text = texts['language:RU']['note'])], [types.KeyboardButton(text = texts['language:RU']['plot'])], [types.KeyboardButton(text = texts['language:RU']['history'])]],resize_keyboard=True),
    'language:EN': types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text = texts['language:EN']['skills']), types.KeyboardButton(text = texts['language:EN']['note'])], [types.KeyboardButton(text = texts['language:EN']['plot'])], [types.KeyboardButton(text = texts['language:EN']['history'])]],resize_keyboard=True)
}
