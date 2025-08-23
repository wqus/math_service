from aiogram import types

#INLINE_BTs
#language buttons
russian_lan_bt = types.InlineKeyboardButton(text='Русский🇷🇺', callback_data='RU')
english_lan_bt = types.InlineKeyboardButton(text='English🇬🇧', callback_data = 'EN')

# INLINE_KBs
kb_language = types.InlineKeyboardMarkup(inline_keyboard=[[russian_lan_bt, english_lan_bt]])
