from datetime import datetime

from google_sheets_telegram_utils.utils import active_user


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


@active_user
def hello(update, context):
    update.message.reply_text('Hello {}!!'.format(update.message.from_user.first_name))


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def test_func(update, context) -> None:
    message = update.message.text
    data = [
        message,
        str(datetime.now()),
    ]
    add_row(data, )

    # parse the message some way
    context.bot.send_message(chat_id=update.effective_chat.id, text='Saved')

