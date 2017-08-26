from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import googlemaps.exceptions as gmaps

from fo_bot import logger, api, rosreest_api
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot import egrn_api, gmaps_api
from fo_bot.settings import *


def summarize(found):
    return (
        f'Адрес: {found.address}\n'
        f'Кадастровый номер: {found.cadnomer}\n'
        f'Площадь: {found.area}\n'
        f'Тип обьекта: {found.property_type}\n'
    )


def write_full_info(full_info):
    return '\n'.join(map(': '.join,
                         map(lambda args: map(str, args),
                             full_info.egrn.details.items())))


@egrn_api.api_error_handler(CABINET)
def read_more(bot, update, *, cadnomer):
    full_info = rosreest_api.get_object_full_info(cadnomer)
    address = full_info.egrn.property_object.address
    try:
        show_map(bot, update, address=address)
    except (gmaps.ApiError, gmaps.TransportError, gmaps.Timeout):
        pass
    update.effective_message.reply_text(
        write_full_info(full_info),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Заказать выписку',
                                                                 callback_data=f'{int(Prefix.ORDER_TYPE)}{cadnomer}'
                                                                 )]])
    )
    return CABINET


def show_map(bot, update, *, address):
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
    bot.send_location(chat_id=update.effective_user.id, latitude=lat, longitude=lng)


@egrn_api.api_error_handler(CABINET)
def search_reestr(bot, update, user_data, *, query):
    logger.info(f'User {update.effective_user.name} made a search query {query}')
    res = rosreest_api.search(query=query)

    if res.found == 0:
        update.message.reply_text('Не найдено ни одного такого обьекта.')
        return CABINET

    update.message.reply_text('Вот что я нашел:')
    if len(res.objects) == 1:
        found = res.objects[0]
        return read_more(bot, update, cadnomer=found.cadnomer)

    for found in res.objects[:5]:
        update.message.reply_text(summarize(found),
                                  reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton(text='Подробнее',
                                                             callback_data=f'{int(Prefix.FULL_DATA)}{found.cadnomer}'
                                                             )]]))
    update.message.reply_text('Если вы не нашли нужный вам обьект, введите более точный адрес.')
    return CABINET


@api_error_handler(CABINET)
def search_fo(bot, update, user_data, *, query):
    logger.info(f'User {update.effective_user.name} made a search query {query}')
    res = api.checkAddres(addres=query, phone=user_data['phone'])

    keyboard = []
    for found in res.values():
        address = found['addres'],
        cadnomer = found['cadNomer']

        keyboard.append([InlineKeyboardButton(text=f'{address} | {cadnomer}',
                                              callback_data=cadnomer
                                              )]
                        )
    #ToDo: gently split keyboard into chunks to fit markup size
    update.message.reply_text('Вот что я нашел:',
                              reply_markup=InlineKeyboardMarkup(keyboard[:20]))
    return ORDER
