from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from ..settings import *


def ask_for_contact(bot, update):
    contact_button = KeyboardButton(text="Отправить мне контакт", request_contact=True)
    update.message.reply_text('Поделитесь своим контактом или введите свой номер телефона, '
                              'под которым вы зарегестрированы на сайте Findtheowner.ru.',
                              reply_markup=ReplyKeyboardMarkup(keyboard=[[contact_button]],
                                                               one_time_keyboard=True)
                              )
    return ASK_PHONE


def fetch_number_from_contact(bot, update, user_data):
    phone = update.message.contact.phone_numbe)
    logger.info(f'User {get_user_name(update)} send a contact with phone number {phone}')

    user_data['phone_number'] = phone
    check_login(bot, update, user_data=user_data)
    return CABINET


def input_phone_number(bot, update):
    update.message.reply_text('Введите телефон:')
    return PHONE
