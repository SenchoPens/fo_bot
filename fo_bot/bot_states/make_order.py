def make_order(bot, update, user_data, *, order_type: OrderType):
    if __debug__:
        update.message.reply_text('Извините, но бот в стадии тестирования, оплата пока не проиводиться.\n'
                                  #f'Номер вашей транзакции: {info.transaction_id}'
                                  )
        cancel_order(bot, update, user_data)
        return CABINET
    order = api.save_order(object_code=user_data['code'], documents=[order_type.api_name])
    info = api.get_transaction_info(order.transaction_id)
    res = api.pay(transaction_id=info.transaction_id,
                  confirm_code=info.pay_method.pa.confirm_code
                  )
    if res.paid:
        update.message.reply_text('Оплата выполнена успешно:\n'
                                  f'Номер заказа: {info.transaction_id}\n'
                                  f'Стоимость: {res.cost}'
                                  )
        user_data['orders'].append(ActiveOrder(id=info.transaction_id, order_type=order_type))
    else:
        update.message.reply_text('Не получилось оплатить заказ. Попробуйте в другой момент.')
    cancel_order(bot, update, user_data)
    return CABINET


@MoneyChecker(ORDERS['xzp'], db=db)
def order_xzp(bot, update, user_data):
    make_order(bot, update, user_data, order_type=ORDERS['xzp'])

@MoneyChecker(ORDERS['sopp'], db=db)
def order_sopp(bot, update, user_data):
    make_order(bot, update, user_data, order_type=ORDERS['sopp'])
