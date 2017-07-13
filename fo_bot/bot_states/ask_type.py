from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from fo_bot.settings import *


def ask_order_type(bot, update):
    keyboard = []
    for type_ in TYPES:
        keyboard.append([
            InlineKeyboardButton(text=type_['text'], callback_data=type_['id'])
        ])
    update.message.reply_text('Вы можете заказать:',
                              reply_markup=InlineKeyboardMarkup(keyboard), one_time_keyboard=True)
    return ORDER
