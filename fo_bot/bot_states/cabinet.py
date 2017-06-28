def search(bot, update):
    text = update.message.text
    query = text[text.find(' ')+1:]
    logger.info(f'User {get_user_name(update)} made a search query {query}')
    res = api.search(query=query)

    if res.found == 0:
        update.message.reply_text('Не найдено ни одного такого обьекта.')
        return CABINET

    keyboard = []
    for found in res.objects:
        cutted_address = found.address[found.address.find(' ул ')+1:-1]  # leave only most important parts
        data = str.encode('|'.join((found.cadnomer, cutted_address)))[:MAX_DATA_LEN].decode()  # cut to fit 64 bytes
        logger.info(data)
        keyboard.append([InlineKeyboardButton(text=f'{found.address} | {found.cadnomer}',
                                              callback_data=data
                                              )]
                        )
    #ToDo: gently split keyboard into chunks to fit markup size
    update.message.reply_text('Вот что я нашел:',
                              reply_markup=InlineKeyboardMarkup(keyboard[:20]))
    return CABINET

def ask_for_confirmation(bot, update, user_data):
    try:
        cadnomer, address = update.callback_query.data.split('|')
    except ValueError:
        update.callback_query.message.reply_text('Извините, произошла какая-то ошибка.\n'''
                                                 'Повторите ваш поиск.')
        return CABINET

    user = update.callback_query.from_user
    logger.info(f'User {user.name} have chosen cadnomer {cadnomer}.')
    user_data['cadnomer'] = cadnomer
    update.callback_query.message.reply_text(f'Вы выбрали {cadnomer}\n'
                                             f'Адрес: {address}\n'
                                             'Заказать выписку?',
                                             reply_markup=ReplyKeyboardMarkup([['Да', 'Нет']],
                                                                              one_time_keyboard=True
                                                                              )
                                             )
    return ASK_ORDER_DOCUMENT

def list_orders(bot, update, user_data):
    orders = user_data['orders']
    if not orders:
        update.message.reply_text('У вас нет заказов в стадии выполнения.')
        return CABINET

    update.message.reply_text('Вот ваши заказы в стадии выполнения:\n')
    for order in orders:
        update.message.reply_text(f'Название услуги: {order.info.name}\n'
                                  f'Стоимость услуги: {order.info.cost}\n'
                                  f'Номер заказа: {order.id}\n'
                                  )


### ASK_ORDER_DOCUMENT ###
def choose_order_type(bot, update, user_data):
    logger.info(f'User {get_user_name(update)} is making an order for cadnomer {user_data["cadnomer"]}')
    object_full_info = api.get_object_full_info(user_data['cadnomer'])

    keyboard = []
    if object_full_info.documents.xzp.available:
        keyboard.append([ORDERS['xzp'].name])
    if object_full_info.documents.sopp.available:
        keyboard.append([ORDERS['sopp'].name])
    if not keyboard:
        update.message.reply_text('Извините, но по этому обьекты нельзя заказать ни одного документа.')
        cancel_chosen(bot, update, user_data)
        return CABINET

    user_data['code'] = object_full_info.encoded_object
    keyboard.append(['Отменить'])
    update.message.reply_text('Выберите услугу:',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                              )
    return ORDER
