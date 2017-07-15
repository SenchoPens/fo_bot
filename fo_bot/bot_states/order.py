from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.settings import *
from fo_bot import api, logger


def ask_order_type(bot, update, user_data):
    print(update.callback_query.data)
    try:
        cadnomer, address = update.callback_query.data.split('|')
    except ValueError:
        update.callback_query.message.reply_text('Извините, произошла какая-то ошибка.\n'''
                                                 'Повторите ваш поиск.')
        return CABINET
    user_data['cadnomer'] = cadnomer

    keyboard = []
    for type_ in TYPES:
        keyboard.append([
            InlineKeyboardButton(text=type_['text'], callback_data=str(type_['id']))
        ])
    update.callback_query.message.reply_text(f'Адрес: {address}\n'
                                             f'Кадастровый номер: {cadnomer}\n'
                                             'Вы можете заказать:',
                                             reply_markup=InlineKeyboardMarkup(keyboard), one_time_keyboard=True)


@api_error_handler(CABINET)
def order_doc(bot, update, user_data):
    logger.info(f'User {update.effective_user.name} made an order.')
    api.addOrder(phone=user_data['phone'], cadast=user_data['cadnomer'],
                 type=update.callback_query.data)
    update.callback_query.message.reply_text('Заказ осущсествлен. Вы можете посмотреть его в '
                                             'вашем личном кабинете на сайте FindTheOwner.ru')
    return CABINET
