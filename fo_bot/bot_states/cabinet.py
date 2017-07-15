from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from fo_bot import logger, api
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.settings import *


def cabinet_help(bot, update):
    update.message.reply_text('Напишите \'баланс\', чтобы проверить свой баланс в любой момент.'
                              '\nНапишите \'искать\' и кадастровый номер или адрес недвижимости, '
                              'на которую вы хотите заказать выписку.'
                              '\nНапишите \'cancel\', чтобы отменить процедуру заказа.'
                              #'\nНапишите \'заказы\', чтобы посмотреть ваши текущие заказы в стадии оплаты.'
                              )


def search_text(bot, update, user_data):
    text = update.message.text
    return _search(bot, update, user_data, query=text[text.find(' ')+1:])


def search_command(bot, update, user_data, args):
    return _search(bot, update, user_data, query=' '.join(args))


@api_error_handler(CABINET)
def _search(bot, update, user_data, *, query):
    logger.info(f'User {update.effective_user.name} made a search query {query}')
    res = api.checkAddres(addres=query, phone=user_data['phone'])

    keyboard = []
    for found in res.values():
        address = found['addres']
        cadnomer = found['cadNomer']

        # leave only most important parts (after street) - assume user knows what town he wants
        compressed_address = address[address.find(' ул ') + 1:-1]
        data = str.encode('|'.join((cadnomer, compressed_address)))[:MAX_DATA_LEN].decode()  # cut to fit 64 bytes
        print(type(data))
        logger.info(data)

        keyboard.append([InlineKeyboardButton(text=f'{address} | {cadnomer}',
                                              callback_data=data
                                              )]
                        )
    #ToDo: gently split keyboard into chunks to fit markup size
    update.message.reply_text('Вот что я нашел:',
                              reply_markup=InlineKeyboardMarkup(keyboard[:20]))
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
