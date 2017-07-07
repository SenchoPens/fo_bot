from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup
)

from fo_bot.settings import *
from fo_bot.bot_states import auth, register
from fo_bot import logger


def fetch_number_from_contact(bot, update, user_data):
    phone = update.message.contact.phone_number
    logger.info(f'User {update.effective.from_user.id} send a contact with phone number {phone}')

    user_data['phone_number'] = phone
    return user_data['chosen'](bot, update, user_data)


def ask_for_contact(bot, update):
    contact_button = KeyboardButton(text="Отправить мне контакт", request_contact=True)
    update.message.reply_text('Поделитесь своим контактом, чтобы я узнал ваш номер телефона',
                              reply_markup=ReplyKeyboardMarkup(keyboard=[[contact_button]],
                                                               one_time_keyboard=True))
    return FETCH_PHONE


def choose_auth(bot, update, user_data):
    user_data['chosen'] = auth.auth
    return ask_for_contact(bot, update)


def choose_register(bot, update, user_data):
    user_data['chosen'] = register.ask_email
    return ask_for_contact(bot, update)
