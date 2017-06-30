from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup
)

from fo_bot.settings import *
from fo_bot.bot_states import auth, register


def ask_for_contact(bot, update):
    contact_button = KeyboardButton(text="Отправить мне контакт", request_contact=True)
    update.message.reply_text('Поделитесь своим контактом или введите свой номер телефона, '
                              'под которым вы зарегестрированы на сайте Findtheowner.ru.',
                              reply_markup=ReplyKeyboardMarkup(keyboard=[[contact_button]],
                                                               one_time_keyboard=True)
                              )
    return ASK_PHONE

def choose_auth(bot, update, user_data):
    user_data['chosen'] = auth.auth
    return ask_for_contact(bot, update)


def choose_register(bot, update, user_data):
    user_data['chosen'] = register.register
    return ASK_PHONE
