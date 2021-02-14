from telegram import Update
from telegram.ext import CallbackContext




def add_thing(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Как назовём эту вещь?")
    return PHOTO

def add_photo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi")



class Thing:

    def __init__(self):
        pass
