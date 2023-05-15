from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from database import sqlite_db as db
from handlers.admin import INLN_KB


async def send_mess_to_admins(message: Message, state: FSMContext, order_id=None):
    data = await state.get_data()
    admins = await db.get_all_admins()

    current_state = await state.get_state()
    print(current_state)

    if "eblan_pay_order" in str(current_state):
        user = data["user_data"]
        msg = (
            f"Пользователь {user[9]}(tg_id: {user[1]}) оплатил заказ под номером {order_id}\n"
            f"Проверьте поступление на счёт!"
        )
        keyboard = await INLN_KB.get_pay_check()
    elif "cancel_order_to_eblan" in str(current_state):
        user = data["user_data"]
        msg = (
            f"Пользователь {user[9]}(tg_id: {user[1]}) отменил заказ под номером {order_id}\n"
            f"Заказ удален из списка заказов!"
        )
        keyboard = None
    else:
        msg = (
            f"Новый заказ под номером: {data['order_id']}\n"
            f"Заказчик: {data['user_username']}"
        )
        keyboard = None

    for admin in admins:
        await message.bot.send_message(
            admin[0],
            msg,
            reply_markup=keyboard
        )
