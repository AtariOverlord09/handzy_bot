from aiogram import executor

from handlers import client, admin, other
from create_bot import DP
from database import sqlite_db


async def online(_):
    print("Бот начал работу")
    sqlite_db.sql_start()


'''*****************************АДМИНСКАЯ ЧАСТЬ****************************'''


'''*****************************ОБЩАЯ ЧАСТЬ****************************'''


def main():
    admin.register_handlers_admin(DP)
    client.register_handlers_client(DP)
    executor.start_polling(DP, skip_updates=True, on_startup=online)


if __name__ == "__main__":
    main()
