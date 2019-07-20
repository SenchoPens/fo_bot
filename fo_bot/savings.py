from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatAction,
)

from fo_bot import (
    user_access,
    saving_orders,
    chat_ids,
    SavingOrder,
    api,
)
from fo_bot.settings import (
    CallbackPrefix,
    ADMIN,
    OVERSEER,
    VALUER,
    SET_VALUE,
    MAIN,
    RECEIVE_TEXT,
)
from fo_bot.ordering import (
    count_tax,
    get_text_info,
    get_cost_field,
)
from fo_bot.decorators import (
    remove_prefix,
    callbackquery_message_to_message,
    need_input,
)
from fo_bot.save_to_docx import save_to_docx
from fo_bot.logger import logger


@need_input(
    receive_state=RECEIVE_TEXT,
    text='Пожалуйста, введите кадастровый номер недвижимости, на которую вы хотите снизить налог:',
)
def propose_saving(update, context):
    cadnumber = context.user_data[need_input.stack_key].pop().text
    logger.info(f'User made saving query with cadnumber {cadnumber}')
    tax = count_tax(cadnumber)

    if not tax:
        update.message.reply_text(
            text=f'К сожалению, стоимость данной недвижимости в реестре неизвестна.'
        )
        return
    update.message.reply_text(
        text=f'Текущий налог на недвижимость с кадастровым номером {cadnumber}:\n{tax}',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text='Рассчитать экономию',
                callback_data=f'{int(CallbackPrefix.COUNT_SAVINGS)}{cadnumber}',
            ),
        ]]),
    )
    return MAIN


def put_admin_task(update, context, *, query):
    for phone, user in user_access.items():
        if user.access_level in (ADMIN, OVERSEER) and user.phone in chat_ids:
            context.bot.send_message(
                chat_id=chat_ids[user.phone],
                text=
                    f'Новая задача от {context.user_data["phone"]}.'
                    f'\nКадастровый номер: {query}.'
                ,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text='Посмотреть результаты оценщиков',
                        callback_data=f'{int(CallbackPrefix.GET_VALUERS_RESULTS)}{query}',
                    ),
                ]])
            )


def put_valuer_task(update, context, *, query):
    for phone, user in user_access.items():
        if user.access_level == VALUER and user.phone in chat_ids:
            context.bot.send_message(
                chat_id=chat_ids[user.phone],
                text=
                    'Новая задача.'
                    f'\nКадастровый номер: {query}.'
                ,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text='Оценить',
                        callback_data=f'{int(CallbackPrefix.SET_VALUE)}{query}',
                    ),
                ]])
            )


@remove_prefix
@callbackquery_message_to_message
def get_valuers_results(update, context):
    query = update.callback_query.data

    order = saving_orders[query]
    text = []
    for phone, user in user_access.items():
        if user.access_level == VALUER:
            if user.phone in order.valuer_results:
                text.append(
                    f'Оценщик {user.name} ({user.phone}) оценил экономию недвижимости '
                    f'{query} в {order.valuer_results[user.phone]}.'
                )
            else:
                text.append(
                    f'Оценщик {user.name} ({user.phone}) еще не оценил экономию недвижимости {query}.'
                )

    update.message.reply_text(
        text='\n'.join(text) + '\n\nНазначить финальную экономию из минимума оценок и послать клиенту файл с результатом',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text='Назначить',
                callback_data=f'{int(CallbackPrefix.SEND_FINAL_RESULT)}{query}'
            )
        ]])
    )


@remove_prefix
@callbackquery_message_to_message
def send_final_result(update, context):
    query = update.callback_query.data

    order = saving_orders[query]
    if not order.valuer_results:
        update.message.reply_text('Ни один оценщик не оценил стоимость недвижимости')
        return

    context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.TYPING)

    info = api.info(code=query)
    info_text = get_text_info(info)

    val_results_list = list(x.rstrip('%') for x in order.valuer_results.values())
    val_results_list.append(val_results_list[0])
    p1, p2, *_ = val_results_list
    res = min(int(p1), int(p2))

    realty_cost = get_cost_field(info)
    economy = round((realty_cost - realty_cost * res / 100) * (0.016 + 0.017), 2)

    doc = save_to_docx(
        info=info_text.replace('*', ''),
        p1=p1,
        p2=p2,
        p3=str(economy),
    )
    with open('demo.docx', 'wb') as f:
        f.write(doc.getvalue())
    doc.seek(0)
    context.bot.send_document(
        document=doc,
        filename='Экономия.docx',
        chat_id=chat_ids[order.user],
        caption=f'Экономия обьека {query} составила {res}%'
    )
    doc.close()


@remove_prefix
@callbackquery_message_to_message
def count_saving(update, context):
    query = update.callback_query.data

    saving_orders[query] = SavingOrder(
        user=context.user_data["phone"],
        cadnumber=query,
        valuer_results=dict(),
        is_finished=False,
    )

    put_admin_task(update, context, query=query)
    put_valuer_task(update, context, query=query)

    update.message.reply_text('Ваш заказ на оценку экономии недвижимости принят нашими экспертами.')
    return None


@remove_prefix
@callbackquery_message_to_message
def input_value(update, context):
    query = update.callback_query.data

    if saving_orders[query].is_finished:
        update.message.reply_text('Заказ уже обработан.')
        return
    update.message.reply_text('Введите вашу оценку:')
    context.user_data['set_value_order'] = query
    return SET_VALUE


def set_value(update, context):
    saving_orders[context.user_data['set_value_order']].valuer_results[context.user_data["phone"]] = update.message.text
    return MAIN
