# -*- coding: utf-8 -*-

import re

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
)

from fo_bot import logger, api, ActionName
from fo_bot.bot_utils.freeze import *
from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.bot_states import (
    register,
    started,
    cabinet,
    order,
    admin,
)

# Enable logging
logger.info('-' * 50)


""" Entry points """


def start(bot, update):
    user = update.effective_user
    logger.info(f'User {user.name} started the conversation.')

    update.message.reply_text(
        f'Здравствуйте, {user.first_name}.\n'
        f'Чтобы завершить разговор, напишите "{ActionName.end.rus}".'
    )
    update.message.reply_text(
        'Вы хотите авторизоваться в существующую учетную запись FindTheOwner.ru,'
        'или зарегестрироваться?',
        reply_markup=ReplyKeyboardMarkup([[ActionName.auth.rus],
                                          [ActionName.register.rus]],
                                         one_time_keyboard=True)
    )
    return ASK_PHONE


""" Fallbacks """


def show_help(bot, update, user_data):
    update.message.reply_text(
        f'Напишите \'/{ActionName.end.eng}\' или \'{ActionName.end.rus}\', чтобы прекратить разговор.'
        f'Напишите \'/{ActionName.show_help.eng}\' или \'{ActionName.show_help.rus}\', чтобы вывести список комманд.'
    )
    if user_data.get('logged', False):
        cabinet.cabinet_help(bot, update)


@api_error_handler(None)
def display_balance(bot, update, user_data):
    if user_data.get('logged', False):
        balance = api.balance(phone=user_data['phone'])['balance']
        update.message.reply_text(f'Ваш баланс: {balance or "0"} рублей.')


def handle_error(bot, update, error):
    """ Error handler """
    logger.warning(f'Update "{update}" caused error "{error}"')


def cancel(bot, update, user_data):
    """ Cancel procedure of logging or ordering (/cancel command) """
    if user_data.get('logged', False):
        return CABINET
    return END


def end(bot, update, user_data):
    """ End conversation (/end command) """
    cancel(bot, update, user_data)
    user_data['logged'] = False
    return END


########################################################################################################################
def cad_pattern(n):
    return '^' + str(int(n)) + r'(\d+:)+\d+$'


def make_rus_regex(name):
    return ''.join(('^', '(', name[0].lower(), '|'))


def make_handler(callback, name, pass_user_data=True):
    english_handler = CommandHandler(name.eng, callback, pass_user_data=pass_user_data)
    russian_handler = RegexHandler(re.compile('^' + name.rus + '$', flags=re.IGNORECASE),
                                   callback, pass_user_data=pass_user_data)
    return [english_handler, russian_handler]


def main():
    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=make_handler(start, ActionName.start),

        states={
            ASK_PHONE: [*make_handler(started.choose_auth, ActionName.auth,
                                      pass_user_data=True),
                        *make_handler(started.choose_register, ActionName.register,
                                      pass_user_data=True),
                        ],
            FETCH_PHONE: [MessageHandler(Filters.contact,
                                         started.fetch_number_from_contact,
                                         pass_user_data=True)
                          ],
            REGISTER: [MessageHandler(Filters.text,
                                      register.register,
                                      pass_user_data=True)
                       ],

            CABINET: [RegexHandler(re.compile(ActionName.search.rus, flags=re.IGNORECASE),
                                   cabinet.search_text,
                                   pass_user_data=True),
                      CommandHandler(ActionName.search.eng,
                                     cabinet.search_command,
                                     pass_user_data=True,
                                     pass_args=True),

                      CallbackQueryHandler(cabinet.read_more_button,
                                           pattern=cad_pattern(Prefix.FULL_DATA)),

                      CallbackQueryHandler(cabinet.ask_order_type,
                                           pattern=cad_pattern(Prefix.ORDER_TYPE),
                                           pass_user_data=True),
                      ],
            ORDER: [CallbackQueryHandler(order.order_doc,
                                         pattern=r'^\d+$',
                                         pass_user_data=True),
                    ],
        },
        fallbacks=[*make_handler(cancel, ActionName.cancel,
                                 pass_user_data=True),

                   *make_handler(end, ActionName.end,
                                 pass_user_data=True),

                   *make_handler(show_help, ActionName.show_help,
                                 pass_user_data=True),

                   *make_handler(display_balance, ActionName.show_balance,
                                 pass_user_data=True),

                   CommandHandler('admin_help', admin.show_admin_help)
                   ]
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(handle_error)

    try:
        dp.user_data = load_user_data()
        conv_handler.conversations = load_conversations()
    except FileNotFoundError:
        logger.warning('user_data or conversations dump file not found')

    if __debug__:
        a = 2
        if a == 1:
            conv_handler.conversations[(182705944, 182705944)] = None
        elif a == 2:
            conv_handler.conversations[(182705944, 182705944)] = 3
            dp.user_data[182705944] = {'phone': '9263793151', 'logged': True, 'orders': []}

    # Start the Bot
    updater.start_polling()

    updater.idle()

    save_conversations(conv_handler.conversations)
    save_user_data(dp.user_data)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error occured: {e}')
        raise e
