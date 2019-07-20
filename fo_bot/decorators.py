from functools import wraps


class need_input:
    _callback_key = '_callback'
    stack_key = 'stack'

    def __init__(self, receive_state, *args, **kwargs):
        self.receive_state = receive_state
        self.reply_args = args
        self.reply_kwargs = kwargs

    @classmethod
    def receive(cls, update, context):
        context.user_data.setdefault(cls.stack_key, [])
        context.user_data[cls.stack_key].append(update.effective_message)

        return context.user_data[cls._callback_key](update, context)

    def __call__(self, f):
        def demand_input(update, context):
            update.effective_message.reply_text(*self.reply_args, **self.reply_kwargs)
            context.user_data[self._callback_key] = f
            return self.receive_state

        f.demand_input = demand_input
        return f


def remove_prefix(f):
    """
    A decorator around callbacks that handle CallbackButton's clicks with cad number in callback data.
    It removes callback type (prefix) from callback data.
    """
    @wraps(f)
    def wrapper(update, context):
        update.callback_query.data = update.callback_query.data[1:]
        return f(update, context)
    return wrapper


def callbackquery_message_to_message(f):
    @wraps(f)
    def wrap(update, context):
        update.message = update.callback_query.message
        return f(update, context)
    return wrap
