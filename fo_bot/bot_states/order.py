from fo_bot.bot_utils.error_handler import api_error_handler
from fo_bot.settings import *
from fo_bot import api, logger, rosreest_api


@api_error_handler(CABINET)
def order_doc(bot, update, user_data):
    logger.info('Started ordering')
    full_info = rosreest_api.get_object_full_info(user_data['cadnomer'])
    address = full_info.egrn.property_object.address
    logger.info(f'User {update.effective_user.name} made an order.')
    api.addOrder(phone=user_data['phone'], cadastr=user_data['cadnomer'],
                 type=update.callback_query.data, addres=address)
    update.callback_query.message.reply_text('Заказ осущсествлен. Вы можете посмотреть его в '
                                             'вашем личном кабинете на сайте FindTheOwner.ru')
    return CABINET
