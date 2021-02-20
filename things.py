from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import uuid
import psycopg2
from psycopg2 import Error


class Thing:

    def __init__(self, name, photo, cost, discount):
        self.name = name
        self.photo = photo
        self.cost = cost
        self.discount = discount
        pass


PHOTO, NAME, COST, DISCOUNT, ACCEPT = range(5)
t1 = Thing(0, 0, 0, 0)


def add_thing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Как назовём эту вещь?")
    return NAME


def add_name(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    t1.name = name
    update.message.reply_text("Окей, давай добавим фотографии " + name)
    return PHOTO


def add_photo(update: Update, context: CallbackContext) -> int:
    if update.message.text:
        if update.message.text.lower().strip() == "стоп":
            update.message.reply_text("Теперь отправь стоимость вещи")
            return COST
        else:
            update.message.reply_text("Не понял тебя, напиши ещё раз.")
    elif update.message.photo:
        try:
            photos = update.message.photo
            file_name = str(uuid.uuid4())
            t1.photo = photos[-1].file_id  # добавить массив фоток
            context.bot.get_file(photos[-1]).download("./photos/" + file_name + ".jpg")
        except Exception:
            print(Exception)
            update.message.reply_text("Опс, что-то пошло не так!")
            return ConversationHandler.END
        finally:
            update.message.reply_text("Фото успешно добавлено.\n"
                                      "Если фото больше нет, отправьте \"Стоп\"")
            return PHOTO
    else:
        update.message.reply_text("Отправь текст или фото")


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
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user="postgres",
                                      # пароль, который указали при установке PostgreSQL
                                      password="15021994",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="discount")

        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # Распечатать сведения о PostgreSQL
        print("Информация о сервере PostgreSQL")
        print(connection.get_dsn_parameters(), "\n")
        # Выполнение SQL-запроса
        cursor.execute("SELECT version();")
        # Получить результат
        record = cursor.fetchone()
        print("Вы подключены к - ", record, "\n")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

    total_price = int(t1.cost) * (100-int(t1.discount)) * 0.01
    print(t1.name)
    print(t1.photo)
    print(t1.cost)
    print(t1.discount)
    print(total_price)
    update.message.reply_text("Итак, вот что у нас получилось: "
                              "\nНазвание - " + t1.name +
                              "\nСтоимость - " + t1.cost +
                              "\nСкидка - " + t1.discount + "%"
                              "\nСтоимость с учётом скидки - " + str(int(total_price)) +
                              "\nФотографии: ")
    context.bot.send_photo(update.message.chat_id, t1.photo)
