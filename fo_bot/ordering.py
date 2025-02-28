import googlemaps as gmaps
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatAction,
)

from fo_bot.logger import logger
from fo_bot.settings import *
from fo_bot import api, gmaps_api
from fo_bot.cabinet import logged_only
from fo_bot.text import ActionName
from fo_bot.decorators import (
    remove_prefix,
    callbackquery_message_to_message,
    need_input,
)


@logged_only
def show_balance(update, context):
    balance = api.balance(phone=context.user_data['phone'])['data']['balance']
    update.message.reply_text(f'Ваш баланс: {balance} рублей.')


@remove_prefix
@callbackquery_message_to_message
@logged_only
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
                callback_data=f'{CallbackPrefix.DOC_TYPE}{i + 1}'
            )
        ])
    context.user_data['cadnomer'] = cadnomer
    update.callback_query.message.reply_text(
        f'Вы выбрали обьект с кадастровым номером: {cadnomer}.' 
        f'\nВы можете заказать:',
        reply_markup=InlineKeyboardMarkup(keyboard),
        one_time_keboard=True
    )
    return MAIN


@callbackquery_message_to_message
@remove_prefix
@logged_only
def order_doc(update, context):
    order_id = update.callback_query.data

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    logger.info(f'User {update.effective_user.name} is making an order {order_id}.')
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


def get_text_info(info):
    return '\n'.join(f'*{key}*: {value}' for key, value in info['details'].items())


def read_more(update, context, *, cadnumber):
    logger.info(f'User {update.effective_user.name} requested info on cadnumber {cadnumber}')

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    info = api.info(code=cadnumber)
    text = get_text_info(info)

    address = info['object']['ADDRESS']
    try:
        show_map(update, context, address=address)
    except (gmaps.exceptions.ApiError, gmaps.exceptions.TransportError, gmaps.exceptions.Timeout) as e:
        logger.warning(f'Gmaps API error: {e}')

    keyboard = \
        [[InlineKeyboardButton(
            text='Заказать выписку',
            callback_data=f'{int(CallbackPrefix.ORDER_TYPE)}{cadnumber}'
        )]]
    tax = count_tax(info['object']['CADNOMER'], info)
    if tax:
        text = text + f'\n\n*Налог на эту недвижимость*:{tax}'
        keyboard.append(
            [InlineKeyboardButton(
                text='На сколько можно понизить налог на эту недвижимость?',
                callback_data=f'{int(CallbackPrefix.COUNT_SAVINGS)}{cadnumber}'
            )]
        )
    update.effective_message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='markdown',
    )
    return MAIN


def get_cost_field(info):
    cost_field_name = 'Кадастровая стоимость'
    if cost_field_name in info['details']:
        logger.info(info['details'])
        cost = info['details'][cost_field_name]
        if not isinstance(cost, float) and not isinstance(cost, int):
            cost = float(cost.replace(',', '.'))

        return cost
    return None



def count_tax(query, info=None):
    if info is None:
        info = api.info(code=query)

    cost = get_cost_field(info)
    if cost is not None:
        return round(cost * 0.016 + cost * 0.017, 2)
    return ''


@need_input(
    receive_state=RECEIVE_TEXT,
    text='Введите адрес или кадастровый номер недвижимости:'
)
def search_reestr(update, context):
    query = context.user_data[need_input.stack_key].pop().text

    logger.info(f'User {update.effective_user.name} made a search query {query}')

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    res = api.search(search=query)['data']

    if len(res) == 0:
        update.message.reply_text('Не найдено ни одного такого обьекта.')
        return MAIN

    update.message.reply_text('Вот что я нашел:')
    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

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


@need_input(
    receive_state=RECEIVE_TEXT,
    text='Введите одно целое число - количество рублей, на которое вы хотите пополнить свой баланс.',
)
@logged_only
def recharge(update, context):
    amount = context.user_data[need_input.stack_key].pop().text
    logger.info(amount)
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