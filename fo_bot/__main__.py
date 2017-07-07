# -*- coding: utf-8 -*-

from re import escape

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

from fo_bot import logger
from fo_bot.bot_utils.freeze import *
from fo_bot.settings import *
from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.bot_utils.api import API
from fo_bot.bot_states import (
    auth,
    register,
    started
)

# Enable logging
logger.info('-' * 50)

api = API()


################################### Helpers ######################################

### Helpers for handlers ###
def get_user_name(update) -> str:
    return update.message.from_user.name


### Additional handlers ###
def check_login(bot, update, user_data):
    pass

def cabinet_help(bot, update):
    update.message.reply_text('Напишите \'баланс\', чтобы проверить свой баланс в любой момент.\n'
                              'Напишите \'искать\' и кадастровый номер или адрес недвижимости, '
                              'на которую вы хотите заказать выписку.\n'
                              'Напишите \'заказы\', чтобы посмотреть ваши текущие заказы в стадии оплаты.'
                              )

def make_cabinet(bot, update, user_data):
    user_data['logged'] = True
    if user_data.get('orders', None) is None:
        user_data['orders'] = []
    cabinet_help(bot, update)

############################# Conversation Handlers ##############################

### entry_points ###
def start(bot, update):
    user_name = update.message.from_user.name
    logger.info(f'User {user_name} started the conversation.')

    update.message.reply_text(
        f'Здравствуйте, {user_name}.\n'
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
    update.message.reply_text('Напишите /cancel или \'завершить\', чтобы прекратить разговор.\n'
                              'Напишите /help, чтобы вывести список комманд.'
                              )
    if user_data['logged']:
        cabinet_help(bot, update)


## If user logged: ##
@api_error_handler(None)
def display_balance(bot, update, user_data):
    if user_data['logged']:
        balance: int = api.balance(phone=user_data['phone_number']).balance
        update.message.reply_text(f'Ваш баланс: {balance} рублей.')


### error handlers ###
def error(bot, update, error):
    logger.warning(f'Update "{update}" caused error "{error}"')


########################################################################################################################

def main():
    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher

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
            '''
            CABINET: [RegexHandler('^(и|И)скать',
                                   search),
                      CallbackQueryHandler(ask_for_confirmation,
                                           pass_user_data=True),
                      RegexHandler('^заказы$',
                                   list_orders,
                                   pass_user_data=True)
                      ],
            ASK_ORDER_DOCUMENT: [RegexHandler('^Нет$',
                                              cancel_chosen,
                                              pass_user_data=True),
                                 RegexHandler('^Да$',
                                              choose_order_type,
                                              pass_user_data=True)
                                 ],
            ORDER: [RegexHandler('^Отменить$',
                                 cancel_order,
                                 pass_user_data=True),
                    RegexHandler(f'^{escape(ORDERS["xzp"].name)}$',
                                 order_xzp,
                                 pass_user_data=True),
                    RegexHandler(f'^{escape(ORDERS["sopp"].name)}$',
                                 order_sopp,
                                 pass_user_data=True)
                    ]
            ''': []
        },
        fallbacks=[#CommandHandler('cancel',
                   #               cancel,
                   #               pass_user_data=True),
                   #RegexHandler('^(з|З)авершить$',
                   #             cancel,
                   #             pass_user_data=True),
                   CommandHandler('help',
                                  show_help,
                                  pass_user_data=True),
                   RegexHandler('^(б|Б)аланс$',
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
        conv_handler.conversations[(182705944, 182705944)] = END

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
