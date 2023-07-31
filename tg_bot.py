from environs import Env
from telegram import Update
from telegram.ext import (
    Updater,
    CallbackContext,
    MessageHandler,
    Filters,
)


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    updater = Updater(env("TG_BOT_TOKEN"))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command, echo
        )
    )

    updater.start_polling()
    updater.idle()
