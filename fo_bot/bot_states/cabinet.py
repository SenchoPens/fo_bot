from functools import wraps

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from fo_bot.bot_utils import search
from fo_bot.settings import *


def remove_prefix(f):
    @wraps(f)
    def wrapper(bot, update, *args, **kwargs):
        update.callback_query.data = update.callback_query.data[1:]
        print(update.callback_query.data)
        return f(bot, update, *args, **kwargs)
    return wrapper


def cabinet_help(bot, update):
    update.message.reply_text('Напишите \'/balance\' или \'баланс\', чтобы проверить свой баланс в любой момент.'
                              '\nНапишите \'/search\' или \'искать\' и кадастровый номер или адрес недвижимости, '
                              'на которую вы хотите заказать выписку.'
                              '\nНапишите \'/cancel\' или \'отменить\', чтобы отменить процедуру заказа.'
                              )


def search_text(bot, update, user_data):
    text = update.message.text
    return search.search_reestr(bot, update, user_data, query=text[text.find(' ') + 1:])


def search_command(bot, update, user_data, args):
    return search.search_reestr(bot, update, user_data, query=' '.join(args))


@remove_prefix
def read_more_button(bot, update):
    return search.read_more(bot, update, cadnomer=update.callback_query.data)


@remove_prefix
def ask_order_type(bot, update, user_data):
    cadnomer = update.callback_query.data

    keyboard = []
    for type_ in TYPES:
        keyboard.append([
            InlineKeyboardButton(text=type_['text'], callback_data=str(type_['id']))
        ])
    user_data['cadnomer'] = cadnomer
    update.callback_query.message.reply_text(f'Вы выбрали обьект с кадастровым номер: {cadnomer}\n'
                                             f'Введите /cancel или \'отменить\', чтобы отменить процедуру заказа.\n'
                                             'Вы можете заказать:',
                                             reply_markup=InlineKeyboardMarkup(keyboard), one_time_keyboard=True)
    return ORDER


def list_orders(bot, update, user_data):
    orders = user_data['orders']
    if not orders:
        update.message.reply_text('У вас нет заказов в стадии выполнения.')
        return CABINET

    update.message.reply_text('Вот ваши заказы в стадии выполнения:\n')
    for order in orders:
        update.message.reply_text(f'Название услуги: {order.info.name}\n'
                                  f'Стоимость услуги: {order.info.cost}\n'
                                  f'Номер заказа: {order.id}\n')
