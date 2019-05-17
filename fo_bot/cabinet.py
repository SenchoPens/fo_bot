from functools import wraps

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from fo_bot.text import ActionName
from fo_bot.logger import logger
from fo_bot.settings import *
from fo_bot import api


def logged_only(f):
    @wraps(f)
    def wrap(update, context):
        if context.user_data['logged']:
            return f(update, context)
        update.message.reply_text(
            'Для использования этой функции вы сначала должны авторизоваться или зарегистрироваться на findtheowner.ru'
        )
        return enter_cabinet(update, context)

    return wrap


def enter_cabinet(update, context):
    update.message.reply_text(
        'Вы хотите авторизоваться (если вы уже зарегестрированы), или зарегестрироваться?',
        reply_markup=ReplyKeyboardMarkup([[ActionName.auth.rus],
                                          [ActionName.register.rus]],
                                         one_time_keyboard=True)
    )
    return MAIN


def ask_email(update, context):
    update.message.reply_text('Введите адрес своей электронной почты:')
    return REGISTER


def register(update, context):
    email = update.message.text
    api.register(phone=context.user_data['phone'], email=email)
    update.message.reply_text('Вы успешно зарегистрировались.')
    return auth(update, context)


def fetch_number_from_contact(update, context):
    phone = update.message.contact.phone_number
    logger.info(f'User {update.effective_user.name} send a contact with phone number {phone}')

    context.user_data['phone'] = phone
    return context.user_data['chosen'](update, context)


def ask_for_contact(update, context):
    contact_button = KeyboardButton(text="Отправить мне контакт", request_contact=True)
    update.message.reply_text(
        'Поделитесь со мной своим номером телефона - это необходимо для авторизации и регистрации.',
        reply_markup=ReplyKeyboardMarkup(keyboard=[[contact_button]],
                                         one_time_keyboard=True)
    )
    return FETCH_PHONE


def choose_auth(update, context):
    context.user_data['chosen'] = auth
    return ask_for_contact(update, context)


def choose_register(update, context):
    context.user_data['chosen'] = ask_email
    return ask_for_contact(update, context)


def make_cabinet(update, context):
    context.user_data['logged'] = True
    if context.user_data.get('orders', None) is None:
        context.user_data['orders'] = []


def auth(update, context):
    api.auth(phone=context.user_data['phone'])
    update.message.reply_text(
        f'Вы успешно вошли в кабинет findtheowner.ru.'
        f'\nТеперь вы можете заказывать выписки, используя свой баланс, который вы можете пополнить командой '
        f'{ActionName.recharge.get_pretty()}.'
        f'\nЧтобы посмотреть свой текущий баланс, наберите {ActionName.show_balance.get_pretty()}.'
    )
    make_cabinet(update, context)
    return MAIN
