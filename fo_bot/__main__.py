# -*- coding: utf-8 -*-

from telegram import (
    ReplyKeyboardMarkup
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

from fo_bot import logger, api
from fo_bot.bot_utils.freeze import *
from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.bot_states import (
    register,
    started,
    cabinet,
    order,
)

# Enable logging
logger.info('-' * 50)


### entry_points ###
def start(bot, update):
    user = update.effective_user
    logger.info(f'User {user.name} started the conversation.')

    update.message.reply_text(
        f'Здравствуйте, {user.first_name}.\n'
        'Чтобы завершить разговор, напишите "Завершить".'
    )
    update.message.reply_text(
        'Вы хотите авторизоваться в существующую учетную запись FindTheOwner.ru,'
        'или зарегестрироваться?',
        reply_markup=ReplyKeyboardMarkup([['Авторизоваться'],
                                          ['Зарегистрироваться']],
                                         one_time_keyboard=True)
    )
    return ASK_PHONE


### fallbacks ###
def show_help(bot, update, user_data):
    update.message.reply_text('Напишите \'/end\' или \'завершить\', чтобы прекратить разговор.'
                              'Напишите \'/help\' или \'помощь\', чтобы вывести список комманд.'
                              )
    if user_data.get('logged', False):
        cabinet.cabinet_help(bot, update)


## If user logged: ##
@api_error_handler(None)
def display_balance(bot, update, user_data):
    if user_data.get('logged', False):
        balance = api.balance(phone=user_data['phone'])['balance']
        update.message.reply_text(f'Ваш баланс: {balance or 0} рублей.')


### error handlers ###
def error(bot, update, error):
    logger.warning(f'Update "{update}" caused error "{error}"')


def cancel(bot, update, user_data):
    if user_data.get('logged', False):
        return CABINET


def end(bot, update, user_data):
    cancel(bot, update, user_data)
    user_data['logged'] = False
    return END


########################################################################################################################
def cad_pattern(n):
    return '^' + str(int(n)) + r'(\d+:)+\d+$'

def main():
    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher
    print(cad_pattern(Prefix.FULL_DATA))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ASK_PHONE: [RegexHandler('^Авторизоваться$',
                                     started.choose_auth,
                                     pass_user_data=True),
                        RegexHandler('^Зарегистрироваться$',
                                     started.choose_register,
                                     pass_user_data=True)
                        ],
            FETCH_PHONE: [MessageHandler(Filters.contact,
                                         started.fetch_number_from_contact,
                                         pass_user_data=True)
                          ],
            REGISTER: [MessageHandler(Filters.text,
                                      register.register,
                                      pass_user_data=True)
                       ],

            CABINET: [RegexHandler('^(и|И)скать',
                                   cabinet.search_text,
                                   pass_user_data=True),
                      CommandHandler('search',
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
        fallbacks=[CommandHandler('cancel',
                                  cancel,
                                  pass_user_data=True),
                   RegexHandler('^отменить$',
                                cancel,
                                pass_user_data=True),

                   RegexHandler('^(з|З)авершить$',
                                end,
                                pass_user_data=True),
                   CommandHandler('end',
                                  end,
                                  pass_user_data=True),

                   CommandHandler('help',
                                  show_help,
                                  pass_user_data=True),
                   RegexHandler('помощь',
                                show_help,
                                pass_user_data=True),

                   RegexHandler('^(б|Б)аланс$',
                                display_balance,
                                pass_user_data=True),
                   CommandHandler('balance',
                                  display_balance,
                                  pass_user_data=True),
                   ]
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

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

    print(dp.user_data)
    print(conv_handler.conversations)
    save_conversations(conv_handler.conversations)
    save_user_data(dp.user_data)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error occured: {e}')
        raise e
