# -*- coding: utf-8 -*-

import re
import sys

from telegram import (
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    RegexHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    PicklePersistence,
)

from fo_bot import api, user_access
from fo_bot.logger import logger
from fo_bot.settings import *
from fo_bot.api import api_error_handler
from fo_bot.pickle_helpers import dump_pickle
from fo_bot.access import AdminControl, ValuerControl
from fo_bot.text import ActionName
from fo_bot.ordering import (
    search_reestr,
    read_more_button,
    ask_order_type,
    order_doc,
    recharge,
    start_recharging,
    show_balance,
)
from fo_bot.cabinet import (
    choose_auth,
    choose_register,
    fetch_number_from_contact,
    register,
)

# Enable logging
logger.info('-' * 50)


""" Entry points """


def start(update, context):
    user = update.effective_user
    context.user_data['logged'] = False
    context.user_data['phone'] = ''
    logger.info(f'User {user.name} started the conversation.')

    update.message.reply_text(
        f'Здравствуйте, {user.first_name}.\n'
    )
    show_help(update, context)
    return MAIN


""" Fallbacks """


def show_help(update, context):
    update.message.reply_text(
        f'Напишите {ActionName.search.get_pretty()} и адрес, чтобы увидеть все обьекты реестра по этому адресу, '
        f'посмотреть по обьектам всю доступную информацию из реестра, а также заказать на какой-нибудь из них выписку.'
        f'\nНапишите {ActionName.search.get_pretty()} и кадастровый номер, чтобы посмотреть всю доступную информацию из реестра '
        f'по обьекту с этим номером, а также заказать на этот обьект выписку.'
        f'\nНапишите {ActionName.show_help.get_pretty()}, чтобы показать эту справку.'
        f'\n\nНапишите {ActionName.show_balance.get_pretty()}, чтобы проверить свой баланс личного кабинета на сайте '
        f'findtheowner.ru.'
        f'\nНапишите {ActionName.recharge.get_pretty()}, чтобы пополнить свой баланс.'
        f'\nНапишите {ActionName.cancel.get_pretty()}, чтобы отменить процедуру заказа выписки.'
        f'\nНапишите {ActionName.end.get_pretty()}, чтобы прекратить наш диалог.'
    )
    phone = context.user_data['phone']
    if phone not in user_access:
        return

    access = user_access[phone].access_level
    if access == OVERSEER:
        update.message.reply_text(
            'Чтобы добавить или удалить администратора, сначала перешлите боту его контакт, '
            'а потом напишите /add_admin, чтобы добавить администратора, или /remove_admin, чтобы удалить.\n'
            'Чтобы посмотреть список логинов всех администраторов, напишите /list_admins.\n'
        )
    if access in (ADMIN, OVERSEER):
        update.message.reply_text(
            'Чтобы добавить или удалить оценщика, сначала перешлите боту его контакт, '
            'а потом напишите /add_valuer, чтобы добавить администратора, или /remove_valuer, чтобы удалить.\n'
            'Чтобы посмотреть список логинов всех оценщиков, напишите /list_valuers.\n'
            'Если вы не знаете, как переслать контакт пользователя, прочитайте статью: '
            'https://telegrammix.ru/kontakty/kak-podelitsya-kontaktom-v-telegramme.html'
        )
    return


def set_contact(update, context):
    contact = update.message.contact
    phone = contact.phone_number
    context.user_data['contact'] = phone
    context.user_data['contact_name'] = contact.first_name + ('' if contact.last_name is None else contact.last_name)
    logger.info(f'Recieved contact {phone} from user {update.effective_user.id} with phone {context.user_data["phone"]}')
    return


def handle_error(update, context):
    """ Error handler """
    logger.warning(f'Update "{update}" caused error "{context.error}"')


def cancel(update, context):
    """ Cancel procedure of logging or ordering (/cancel command) """
    return MAIN


def end(update, context):
    """ End conversation (/end command) """
    cancel(update, context)
    context.user_data['logged'] = False
    return END


########################################################################################################################
def cad_pattern(n: CallbackPrefix):
    """Make a regex pattern for callback data with cad number and type of callback (prefix) in int"""
    return '^' + str(int(n)) + r'(\d+:)+\d+$'


def make_handler(callback, name):
    russian_handler = MessageHandler(Filters.regex(re.compile('^' + name.rus, flags=re.IGNORECASE)), callback)
    return russian_handler


def main():
    pp = PicklePersistence(filename='fobot_persistance.persistance')

    if 'proxy' in sys.argv:
        logger.info(f'Starting in PROXY mode. Proxy URL: {REQUEST_KWARGS["proxy_url"]}')
        request_kwargs=REQUEST_KWARGS
    else:
        logger.info('Starting in NORMAL mode')
        request_kwargs = None

    updater = Updater(
        token=BOT_TOKEN,
        request_kwargs=request_kwargs,
        persistence=pp,
        use_context=True,
    )

    admin_control = AdminControl((OVERSEER,), ADMIN, user_access)
    valuer_control = ValuerControl((OVERSEER, ADMIN), VALUER, user_access)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],

        states={
            FETCH_PHONE: [
                MessageHandler(Filters.contact, fetch_number_from_contact),
            ],
            REGISTER: [
                MessageHandler(Filters.text, register),
            ],
            MAIN: [
                make_handler(search_reestr, ActionName.search),
                make_handler(choose_auth, ActionName.auth),
                make_handler(choose_register, ActionName.register),
                make_handler(show_balance, ActionName.show_balance),
                make_handler(start_recharging, ActionName.recharge),

                CallbackQueryHandler(read_more_button, pattern=cad_pattern(CallbackPrefix.FULL_DATA)),
                CallbackQueryHandler(ask_order_type, pattern=cad_pattern(CallbackPrefix.ORDER_TYPE)),
                CallbackQueryHandler(order_doc, pattern=f'^{CallbackPrefix.DOC_TYPE}\d+$'),

                CommandHandler('list_admins', admin_control.list),
                CommandHandler('list_valuers', valuer_control.list),
                CommandHandler('add_admin', admin_control.add),
                CommandHandler('add_valuer', valuer_control.add),
                CommandHandler('remove_admin', admin_control.remove),
                CommandHandler('remove_valuer', valuer_control.remove),

                MessageHandler(Filters.contact, set_contact),
            ],
            RECHARGE: [
                MessageHandler(Filters.text, recharge)
            ],
        },
        fallbacks=[
            make_handler(cancel, ActionName.cancel),
            make_handler(end, ActionName.end),
            make_handler(show_help, ActionName.show_help),
        ],
        #per_message=True,
        name='fobot_conversation',
        persistent=True,
    )
    dp.add_handler(conv_handler)

    user_access_controllers = [
    ]
    for handler in user_access_controllers:
        dp.add_handler(handler)

    # log all errors
    dp.add_error_handler(handle_error)

    if 'debug-start' in sys.argv:
        conv_handler.conversations[(182705944, 182705944)] = None
        dp.user_data[182705944] = {}
    elif 'debug-huh' in sys.argv:
        conv_handler.conversations[(182705944, 182705944)] = 3
        dp.user_data[182705944] = {'phone': '+79263793151', 'logged': True, 'orders': []}

    logger.info('Starting the bot...')
    # Start the Bot
    updater.start_polling()

    updater.idle()

    user_access.close()
    logger.info('The bot has stopped.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error occured: {e}')
        raise e
