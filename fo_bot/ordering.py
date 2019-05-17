from functools import wraps

import googlemaps as gmaps
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatAction,
)

from fo_bot.logger import logger
from fo_bot.api import api_error_handler
from fo_bot.settings import *
from fo_bot import api, gmaps_api, rosreest_api
from fo_bot.cabinet import logged_only
from fo_bot.text import ActionName
import fo_bot.egrn_api as egrn_api


@logged_only
@api_error_handler(None)
def show_balance(update, context):
    balance = api.balance(phone=context.user_data['phone'])['data']['balance']
    update.message.reply_text(f'Ваш баланс: {balance} рублей.')


def remove_prefix(f):
    """
    A decorator around callbacks that handle CallbackButton's clicks with cad number in callback data.
    It removes callback type (prefix) from callback data.
    """
    @wraps(f)
    def wrapper(update, context):
        update.callback_query.data = update.callback_query.data[1:]
        return f(update, context)
    return wrapper


@remove_prefix
def read_more_button(update, context):
    return read_more(update, context, cadnumber=update.callback_query.data)


@remove_prefix
def ask_order_type(update, context):
    cadnomer = update.callback_query.data

    keyboard = []
    services = api.service()['data']
    logger.info(services)
    for i, service in enumerate(services):
        keyboard.append([
            InlineKeyboardButton(
                text=f'{service["name"]} ({service["price"]})',
                callback_data=f'{CallbackPrefix.DOC_TYPE}{i}'
            )
        ])
    context.user_data['cadnomer'] = cadnomer
    update.callback_query.message.reply_text(
        f'Вы выбрали обьект с кадастровым номер: {cadnomer}.' 
        f'\nВведите {ActionName.cancel.get_pretty()}, чтобы отменить процедуру заказа.' 
        f'\nВы можете заказать:',
        reply_markup=InlineKeyboardMarkup(keyboard),
        one_time_keboard=True
    )
    return MAIN


@remove_prefix
@logged_only
@api_error_handler(MAIN)
def order_doc(update, context):
    order_id = update.callback_query.data

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    res = api.order(phone=context.user_data['phone'], number=context.user_data['cadnomer'],
                    service=order_id)
    if 'pay' in res:
        link = res['pay']['link']
        update.callback_query.message.reply_text(
            f'У вас недостаточно денег на балансе для совершения заказа. Ссылка для пополнения баланса: {link}'
        )
        return MAIN

    logger.info(f'User {update.effective_user.name} made an order {order_id}.')
    update.callback_query.message.reply_text(
        'Заказ осуществлен. Вы можете посмотреть его в ' 
        'вашем личном кабинете на сайте findtheowner.ru.'
    )
    return MAIN


@logged_only
def list_orders(update, context):
    orders = context.user_data['orders']
    if not orders:
        update.message.reply_text('У вас нет заказов в стадии выполнения.')
        return MAIN

    update.message.reply_text('Вот ваши заказы в стадии выполнения:')
    for order in orders:
        update.message.reply_text(
            f'\nНазвание услуги: {order.info.name}'
            f'\nСтоимость услуги: {order.info.cost}'
            f'\nНомер заказа: {order.id}'
        )


def summarize(found):
    return (
        f'Адрес: {found["address"]}\n'
        f'Кадастровый номер: {found["number"]}\n'
    )


def show_map(update, context, *, address):
    address_parts = address.split(',')
    house_part = [i for i, p in enumerate(address_parts) if ' д ' in p]
    house_address = ','.join(address_parts[:(len(house_part) and house_part[0]
                                             or len(address_parts)) + 1])
    res = gmaps_api.geocode(address)
    if not res:
        return

    gmaps_resp = res[0]
    gmaps_location = gmaps_resp['geometry']['location']
    lat, lng = gmaps_location['lat'], gmaps_location['lng']
    context.bot.send_location(chat_id=update.effective_user.id, latitude=lat, longitude=lng)


@api_error_handler(MAIN)
def read_more(update, context, *, cadnumber):
    logger.info(f'User {update.effective_user.name} requested info on cadnumber {cadnumber}')

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    info = api.info(code=cadnumber)
    address = info['address']

    try:
        show_map(update, context, address=address)
    except (gmaps.exceptions.ApiError, gmaps.exceptions.TransportError, gmaps.exceptions.Timeout) as e:
        logger.warning(f'Gmaps API error: {e}')

    update.effective_message.reply_text(
        text='\n'.join(': '.join(args) for args in info.items()),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                text='Заказать выписку',
                callback_data=f'{int(CallbackPrefix.ORDER_TYPE)}{cadnumber}'
            )]]
        )
    )
    return MAIN


@egrn_api.api_error_handler(MAIN)
def read_more_egrn(update, context, *, cadnumber):
    logger.info(f'User {update.effective_user.name} requested info on cadnumber {cadnumber}')

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    info = rosreest_api.get_object_full_info(cadnumber)
    address = info.egrn.property_object.address
    try:
        show_map(update, context, address=address)
    except (gmaps.exceptions.ApiError, gmaps.exceptions.TransportError, gmaps.exceptions.Timeout) as e:
        logger.warning(f'Gmaps API error: {e}')
    update.effective_message.reply_text(
        text='\n'.join(': '.join(args) for args in info.egrn.details.items()),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Заказать выписку',
                                                                 callback_data=f'{int(CallbackPrefix.ORDER_TYPE)}{cadnumber}'
                                                                 )]])
    )
    return MAIN


@api_error_handler(MAIN)
def search_reestr(update, context):
    text = update.message.text
    query = text[text.find(' ') + 1:]

    logger.info(f'User {update.effective_user.name} made a search query {query}')

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    res = api.search(search=query)['data']

    if len(res) == 0:
        update.message.reply_text('Не найдено ни одного такого обьекта.')
        return MAIN

    update.message.reply_text('Вот что я нашел:')
    if len(res) == 1:
        found = res[0]
        return read_more(update, context, cadnumber=found['number'])

    for found in res[:5]:
        update.message.reply_text(
            summarize(found),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    text='Подробнее',
                    callback_data=f'{int(CallbackPrefix.FULL_DATA)}{found["number"]}'
                )]]
            )
        )

    update.message.reply_text('Если вы не нашли нужный вам обьект, введите более точный адрес.')
    return MAIN


@logged_only
def start_recharging(update, context):
    update.message.reply_text(
        'Введите одно целое число - количество рублей, на которое вы хотите пополнить свой баланс.'
    )
    return RECHARGE


@api_error_handler(MAIN)
def recharge(update, context):
    amount = update.message.text[:10]
    try:
        amount = int(amount)
    except ValueError:
        update.message.reply_text(
            f'Пожалуйста, введите одно целое число - количество рублей, на которое вы хотите пополнить свой баланс, '
            f'или введите {ActionName.cancel.get_pretty()}, чтобы отменить процедуру пополнения баланса.'
        )
        return

    link = api.recharge(phone=context.user_data['phone'], amount=amount)['pay']['link']
    update.message.reply_text(
        f'Перейдите по этой ссылке для пополнения баланса:'
        f'\n{link}'
    )
    return MAIN