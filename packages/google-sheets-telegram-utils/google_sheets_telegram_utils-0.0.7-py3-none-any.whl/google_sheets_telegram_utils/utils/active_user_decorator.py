from functools import wraps
from typing import Callable

from google_sheets_telegram_utils.exceptions import RowDoesNotExistException
from google_sheets_telegram_utils.utils.classes import TelegramUser
from google_sheets_telegram_utils.utils.connectors.abstract_connector import AbstractConnector


def active_user(google_connector: AbstractConnector):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update, context):
            pk = update.message.from_user.id
            try:
                data = await google_connector.get_row_by_id(pk=pk)
            except RowDoesNotExistException:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, you are not registered yet",
                )
            else:
                user = TelegramUser(data)
                if not user.is_activated:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Sorry, Admin has not activated you yet",
                    )
                else:
                    return await func(update, context)
        return wrapper
    return decorator
