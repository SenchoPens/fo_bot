from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot import logger, api


@api_error_handler
def auth(bot, update, user_data):
    api.auth(phone=user_data['phone'], email=user_data['email'])


def fetch_number_from_contact(bot, update, user_data):
    phone = update.message.contact.phone_number
    logger.info(f'User {get_user_name(update)} send a contact with phone number {phone}')

    user_data['phone_number'] = phone
    check_login(bot, update, user_data=user_data)
    return CABINET


def input_phone_number(bot, update):
    update.message.reply_text('Введите телефон:')
    return PHONE
