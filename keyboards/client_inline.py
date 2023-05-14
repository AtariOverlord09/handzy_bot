from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import sqlite_db as db


# Создаем инлайн клаву для отмены заявки.
cancel_kb = InlineKeyboardMarkup()
cancel_but = InlineKeyboardButton(
    text="Главное меню",
    callback_data="cancel",
)
cancel_kb.add(cancel_but)


# Создаем инлайн клаву для отправки, редактирования или отмены заявки
cancel_or_approve = InlineKeyboardMarkup(row_width=2)
approve_but = InlineKeyboardButton(
    text="Отправить заявку",
    callback_data="approve",
)
edit_url = InlineKeyboardButton(
    text="Изменить ссылку",
    callback_data="edit_url",
)
edit_size = InlineKeyboardButton(
    text="Изменить размер",
    callback_data="edit_size",
)
edit_cost = InlineKeyboardButton(
    text="Изменить стоимость",
    callback_data="edit_cost",
)
edit_info = InlineKeyboardButton(
    text="Изменить доп. инфо",
    callback_data="edit_info",
)
cancel_or_approve.add(
    approve_but,
).add(
    edit_url,
    edit_size,
    edit_cost,
    edit_info,
).add(
    cancel_but,
)


# Создаем клавиатуру для вопроса о ссылке на товар.
url_question_kb = InlineKeyboardMarkup(row_width=1)
url_question_but = InlineKeyboardButton(
    text="Где найти ссылку на товар?",
    url=(
        "https://www.youtube.com/watch?v=gpCIfQUbYlY&list"
        "=PLNi5HdK6QEmX1OpHj0wvf8Z28NYoV5sBJ&index=9"
    ),
)
url_question_kb.add(url_question_but)
url_question_kb.add(cancel_but)


# Создаем клавиатуру для редактирвоания пункта ссылки
url_edit = InlineKeyboardMarkup(row_width=1)
go_back = InlineKeyboardButton(
    text="Назад",
    callback_data="back",
)
url_edit.add(url_question_but, cancel_but, go_back)


# Создаем клавиатуру для вопроса о размере обуви.
size_kb = InlineKeyboardMarkup(row_width=1)
size_but = InlineKeyboardButton(
    text="Как узнать нужный размер товара?",
    url=(
        "https://www.youtube.com/watch?v=gpCIfQUbYlY&list"
        "=PLNi5HdK6QEmX1OpHj0wvf8Z28NYoV5sBJ&index=9"
    ),
)
size_kb.add(size_but)
size_kb.add(cancel_but)


# Создаем клавиатуру для пропуска ввода доп. информации
# skip_kb = InlineKeyboardMarkup()
# skip_but = InlineKeyboardButton(
#     text="Пропустить",
#
# )


# Создаем клавиатуру для просмотра профиля
profile_kb = InlineKeyboardMarkup(row_width=1)
edit_name_but = InlineKeyboardButton(
    text="Изменить имя",
    callback_data="ch_name"
)
view_order = InlineKeyboardButton(
    text="Посмотреть заказы",
    callback_data="view_order",
)
sync_but = InlineKeyboardButton(
    text="Посмотреть ключи синхронизации",
    callback_data="sync",
)
profile_kb.add(edit_name_but, view_order, sync_but, cancel_but)


# Создаем клавиатуру для изменения имени
name_change = InlineKeyboardMarkup(row_width=1)
name_change.add(go_back, cancel_but)


# order_view_kb = InlineKeyboardMarkup(row_width=2)
# next_list = InlineKeyboardButton(
#     text="Далее",
#     callback_data="next",
# )
# order_view_kb.add(go_back, next_list)


def get_keyboard(user_id, current_page):
    keyboard = InlineKeyboardMarkup(row_width=2)
    total_pages = db.get_orders_count(user_id)
    if current_page > 1:
        prev_page_btn = InlineKeyboardButton("<<", callback_data=f"order_pg#{current_page-1}")
        keyboard.add(prev_page_btn)
    if current_page < total_pages:
        next_page_btn = InlineKeyboardButton(">>", callback_data=f"order_pg#{current_page+1}")
        keyboard.insert(next_page_btn)
    return keyboard


actual_course_kb = InlineKeyboardMarkup(row_width=1)
how_price_url = InlineKeyboardButton(text="Как узнать стоимость товара?", url="https://chat.openai.com/")
actual_course_kb.add(how_price_url).add(cancel_but)


poizon_install_kb = InlineKeyboardMarkup(row_width=1)
how_poizon_url = InlineKeyboardButton(text="Как установить POIZON?", url="https://chat.openai.com/")
poizon_install_file = InlineKeyboardButton(text="Скачать POIZON", callback_data="install")
poizon_install_kb.add(how_poizon_url, poizon_install_file).add(cancel_but)


support_kb = InlineKeyboardMarkup(row_width=1)
support_but = InlineKeyboardButton(text="Служба поддержки", url="https://chat.openai.com/")
support_kb.add(support_but).add(cancel_but)
