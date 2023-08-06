import logging


from google_sheets_telegram_utils.handlers import *
from telegram.ext import Updater, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('hello', hello))

    dp.add_handler(CommandHandler('register', register_handler))
    # handle everything that starts with 'Test'
    # dp.add_handler(MessageHandler(Filters.regex(f'^(?i)(Test)'), test_func))
    # dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
