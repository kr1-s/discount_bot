import psycopg2
from psycopg2 import Error, errors
from psycopg2._psycopg import cursor
from psycopg2.sql import SQL
from main import logger

conn: psycopg2 = psycopg2.connect(user="postgres",
                                  # пароль, который указали при установке PostgreSQL
                                  # password="15021994",
                                  host="localhost",
                                  port="5432",
                                  database="discount")


def registration(user_id, username, first_name, last_name) -> None:
    conn.cursor().execute(
        "INSERT INTO public.users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
        (user_id, username, first_name, last_name,))
    conn.commit()
    conn.close()
    logger.info("Пользователь %s:%s зарегистрирован", username, user_id)


def insert_thing(user_id, name, cost, discount, photo) -> None:
    conn.cursor().execute(
        "INSERT INTO public.things (user_id, name, cost, discount) VALUES (%s, %s, %s, %s)",
        (user_id, name, cost, discount,))
    conn.commit()
    conn.close()
