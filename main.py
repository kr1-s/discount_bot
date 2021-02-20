#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import psycopg2
from psycopg2 import Error, sql
from psycopg2._psycopg import cursor
from psycopg2.sql import SQL

import things
from things import add_thing, add_photo, add_cost, add_name, add_discount, accept_thing
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    reg = [[InlineKeyboardButton("Регистрация", callback_data='reg')]]
    update.message.reply_text("Привет, я бот и я помогу тебе определиться в покупкой вещей. Просто следуй моим "
                              "инструкциям.\n"
                              "Для начала нажми на кнопку *Регистрация.", reply_markup=InlineKeyboardMarkup(reg))


def welcome(update: Update, context: CallbackContext) -> None:
    user = update.callback_query.from_user
    update.callback_query.from_user.send_message("Приятно познакомиться %s" % user.first_name)
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user="postgres",
                                      # пароль, который указали при установке PostgreSQL
                                      password="15021994",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")
        insert_query = SQL("INSERT INTO users (username, first_name, last_name) VALUES (%s, %s, %s);")
        print(sql.SQL(insert_query), (user.username, user.first_name, user.last_name,))
        cursor.execute(insert_query, (user.username, user.first_name, user.last_name,))
        connection.commit()
        print("1 запись успешно вставлена")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1382236154:AAGYgwaHWxI_F03b6ptqcx1fbNYjLMpFrnk", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(welcome))
    # on noncommand i.e message - echo the message on Telegram
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_thing)],
        states={
            things.NAME: [MessageHandler(Filters.text, add_name)],
            things.PHOTO: [MessageHandler(Filters.photo | Filters.text, add_photo)],
            things.COST: [MessageHandler(Filters.text, add_cost)],
            things.DISCOUNT: [MessageHandler(Filters.text, add_discount)]
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
