from dataclasses import dataclass
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from fo_bot.logger import logger


@dataclass(frozen=True)
class User:
    access_level: int
    name: str
    phone: str


class UserControl:
    """Interface that provides authorized control of some group of users by other groups of users"""

    _nobody = User(access_level=-1, name='', phone='')

    def __init__(self, access_levels, controlled_object, user_access):
        self.access_levels = access_levels
        self.user_access = user_access
        self.controlled_object = controlled_object

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if not hasattr(attr, '__call__'):
            return attr
        f = attr

        @wraps(f)
        def wrapped(update: Update, context: CallbackContext):
            phone = context.user_data.get('phone', '')
            if self.user_access.get(phone, self._nobody).access_level not in self.access_levels:
                logger.warning(f'Attempt to access {f.__name__} by user {phone}')
                return
            logger.info(f'Access granted to {f.__name__} for user {phone}')
            return f(update, context)

        return wrapped

    def list(self, update: Update, context: CallbackContext):
        objects = [user.name for user in self.user_access.values() if user.access_level == self.controlled_object]
        if objects:
            update.message.reply_text('\n'.join(objects))
        else:
            update.message.reply_text('Список пуст')
        return

    def remove(self, update: Update, context: CallbackContext):
        if 'contact' not in context.user_data:
            update.message.reply_text('Пожалуйста, сначало перешлите пользователя боту.')
            return
        phone = context.user_data['contact']
        if phone not in self.user_access:
            update.message.reply_text('Пользователь с таким номером телефона не найден среди списка.')
            return
        del self.user_access[phone]
        logger.info(f'User {context.user_data["phone"]} removed {phone} from {type(self).__name__}.')
        return

    def add(self, update: Update, context: CallbackContext):
        if 'contact' not in context.user_data:
            update.message.reply_text('Пожалуйста, сначало перешлите пользователя боту.')
            return
        phone = context.user_data['contact']
        # Assume the bigger the number under privilege, the bigger access is granted
        self.user_access[phone] = User(
            access_level=max(self.controlled_object, self.user_access.get(phone, -1)),
            name=context.user_data['contact_name'],
            phone=phone,
        )
        logger.info(f'User {context.user_data["phone"]} added {phone} to {type(self).__name__}.')


class AdminControl(UserControl):
    pass


class ValuerControl(UserControl):
    pass
