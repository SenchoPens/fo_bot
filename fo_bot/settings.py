# Telegram API
BOT_TOKEN = '342476710:AAG0fW1kmSiAYCbNl-IlzjmN8VjJK9aRt5w'
MAX_DATA_LEN = 64

# Bot
END, STARTED, ASK_PHONE, PHONE, CABINET, ASK_ORDER_CONFIRMATION, ASK_ORDER_DOCUMENT, ORDER = range(-1, 7)
CONVERSATION_DUMP_FILENAME = 'bot_user_conversations.pickle'
USER_DATA_DUMP_FILENAME = 'bot_user_data.pickle'

# Rosreestr API
'''
ORDERS: Dict[str, OrderType] = {'xzp': OrderType(name='Электронная выписка (ЭВ) (250р.)',
                                                 cost=250,
                                                 api_name='XZP'
                                                 ),
                                  'sopp': OrderType(name='Электронная выписка о переходе прав (250р.)',
                                                    cost=250,
                                                    api_name='SOPP'
                                                    )
                                }
'''
API_TOKEN = '9AEE-ZLJY-QJAN-DXF7'
