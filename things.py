from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
import uuid
import psycopg2
from psycopg2 import Error
import sql


class Thing:

    def __init__(self, name, photo, cost, discount):
        self.name = name
        self.photo = [photo]
        self.cost = cost
        self.discount = discount
        pass


PHOTO, NAME, COST, DISCOUNT, ACCEPT = range(5)
t1 = Thing(0, 0, 0, 0)
t1.photo.clear()


def add_thing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Как назовём эту вещь?")
    return NAME


def add_name(update: Update, context: CallbackContext) -> int:
    stop_buttons = [[KeyboardButton('Стоп')]]
    name = update.message.text
    t1.name = name
    update.message.reply_text("Окей, давай добавим фотографии \"%s\".\n"
                              "Как закончишь нажми кнопку \"Стоп\"" % name,
                              reply_markup=ReplyKeyboardMarkup(stop_buttons,
                                                               resize_keyboard=True,
                                                               one_time_keyboard=True))
    return PHOTO


def add_photo(update: Update, context: CallbackContext) -> int:

    if update.message.text:
        if update.message.text.lower().strip() == "стоп":
            update.message.reply_text("Теперь отправь стоимость вещи", reply_markup=ReplyKeyboardRemove())
            return COST
        else:
            update.message.reply_text("Не понял тебя, напиши ещё раз.")
    elif update.message.photo:
        try:
            photos = update.message.photo
            file_name = str(uuid.uuid4())
            t1.photo.append(photos[-1].file_id)  # добавить массив фоток
            context.bot.get_file(photos[-1]).download("./photos/" + file_name + ".jpg")
            return PHOTO
        except Exception:
            print(Exception)
            update.message.reply_text("Опс, что-то пошло не так!")
            return ConversationHandler.END

    else:
        update.message.reply_text("Нажми \"Стоп\" или отправь фото")


def add_cost(update: Update, context: CallbackContext) -> int:
    cost = update.message.text
    t1.cost = cost
    update.message.reply_text("Отправьте размер (%) скидки ")
    return DISCOUNT


def add_discount(update: Update, context: CallbackContext) -> int:
    discount = update.message.text
    t1.discount = discount
    accept_thing(update, context)
    return ConversationHandler.END


def accept_thing(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    total_price = int(t1.cost) * (100 - int(t1.discount)) * 0.01
    print(t1.name)
    for id in t1.photo:
        print(id)
    print(t1.cost)
    print(t1.discount)
    print(total_price)
    sql.insert_thing(user.id, t1.name, t1.cost, t1.discount, t1.photo)

    update.message.reply_text("Итак, вот что у нас получилось: "
                              "\nНазвание - " + t1.name +
                              "\nСтоимость - " + t1.cost +
                              "\nСкидка - " + t1.discount + "%"
                                                            "\nСтоимость с учётом скидки - " + str(int(total_price)) +
                              "\nФотографии: ")
    for id in t1.photo:
        context.bot.send_photo(update.message.chat_id, photo=id)
