from google_sheets_telegram_utils.exceptions import RowDoesNotExistException
from google_sheets_telegram_utils.utils.classes import TelegramUser
from google_sheets_telegram_utils.utils.connectors.abstract_connector import AbstractConnector


class HandlerFactory:
    @staticmethod
    def get_register_handler(connector: AbstractConnector):
        async def register_handler(update, context):
            telegram_user = update.message.from_user
            try:
                await connector.get_row_by_id(telegram_user.id)
            except RowDoesNotExistException:
                try:
                    telegram_user = TelegramUser.from_telegram_user(telegram_user)
                    await connector.add_row(telegram_user.convert_to_list())
                except Exception as err:  # TODO use more specific exception
                    await update.message.reply_text('Cannot register now :c')
                else:
                    await update.message.reply_text('You have been registered. Admin will activate you soon, maybe :3')
            else:
                await update.message.reply_text('You are already registered.')
        return register_handler
