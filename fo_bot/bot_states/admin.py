from .. import ActionName, restricted


@restricted
def show_admin_help(bot, update):
    update.effective_message.reply_text(
        f'Чтобы выйти, наберите \'{ActionName.cancel.rus}\' или \'/{ActionName.cancel.eng}\'.'
        f'\nЧтобы изменить стоимость выписки, наберите \'/{ActionName.change_cost.eng}\'.',
    )


@restricted
def change_cost(bot, update):
    pass
