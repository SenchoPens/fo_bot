from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from fo_bot.settings import *


def ask_order_type(bot, update):
    try:
        cadnomer, address = update.callback_query.data.split('|')
    except ValueError:
        update.callback_query.message.reply_text('Извините, произошла какая-то ошибка.\n'''
                                                 'Повторите ваш поиск.')
        return CABINET


    keyboard = []
    for type_ in TYPES:
        keyboard.append([
            InlineKeyboardButton(text=type_['text'], callback_data=type_['id'])
        ])
    update.message.reply_text(f'Адрес: {address}\n'
                              f'Кадастровый номер: {cadnomer}\n'
                              'Вы можете заказать:',
                              reply_markup=InlineKeyboardMarkup(keyboard), one_time_keyboard=True)
    return ORDER
