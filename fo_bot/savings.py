from dataclasses import dataclass

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatAction,
)

from fo_bot import (
    user_access,
    saving_orders,
    chat_ids,
)
from fo_bot.settings import (
    CallbackPrefix,
    ADMIN,
    OVERSEER,
    VALUER,
    SET_VALUE,
    MAIN,
)
from fo_bot.ordering import (
    count_tax,
)
from fo_bot.decorators import (
    remove_prefix,
    callbackquery_message_to_message,
)
from fo_bot.logger import logger


@dataclass()
class SavingOrder:
    user: str
    cadnumber: str
    valuer_results: dict
    is_finished: bool


def propose_saving(update, context):
    text = update.message.text
    query = text[text.find(' ') + 1:]

    tax = count_tax(query)

    if not tax:
        update.message.reply_text(
            text=f'К сожалению, стоимость данной недвижимости в реестре неизвестна.'
        )
        return
    update.message.reply_text(
        text=f'Текущий налог на недвижимость с кадастровым номером {query}:\n{tax}',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text='Рассчитать экономию',
                callback_data=f'{int(CallbackPrefix.COUNT_SAVINGS)}{query}',
            ),
        ]]),
    )


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
    res = min(int(x.rstrip('%')) for x in order.valuer_results.values())
    context.bot.send_message(
        chat_id=chat_ids[order.user],
        text=f'Экономия обьека {query} составила {res}%'
    )


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
    update.message.reply_text('Введите вашу оценку, или введите /cancel:')
    context.user_data['set_value_order'] = query
    return SET_VALUE


def set_value(update, context):
    saving_orders[context.user_data['set_value_order']].valuer_results[context.user_data["phone"]] = update.message.text
    return MAIN
