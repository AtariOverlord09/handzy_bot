from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import sqlite_db as db


class InlineAdminKeyboard:
    def __init__(self):

        self.main_manu_button = InlineKeyboardButton(
            text="Главное меню",
            callback_data="main_menu",
        )
        self.comission_course_kb = InlineKeyboardMarkup(row_width=2)
        self.comission_course_kb.add(
            InlineKeyboardButton(
                text='Изменить курс и комиссию',
                callback_data='all_change',
            ),
        )
        self.comission_course_kb.add(
            InlineKeyboardButton(
                text='Изменить только комиссию',
                callback_data='comission_change',
            ),
            InlineKeyboardButton(
                text='Изменить только курс',
                callback_data='course_change',
            ),
        )
        self.comission_course_kb.add(
            InlineKeyboardButton(
                text="Посмотреть акутальный курс юаня",
                callback_data='check_uan',
            ),
        )

        self.back_kb = InlineKeyboardMarkup(row_width=1)
        self.back_kb.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data="back",
            ),
        )

        self.accept_card_kb = InlineKeyboardMarkup(row_width=2)
        self.accept_card_kb.add(
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data="accept_card",
            ),
            InlineKeyboardButton(
                text="Отменить",
                callback_data="cancel_card",
            ),
        )

        self.poizon_load_kb = InlineKeyboardMarkup(row_width=2)
        self.poizon_load_kb.add(
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data="accept_apk",
            ),
            InlineKeyboardButton(
                text="Отменить",
                callback_data="cancel_apk",
            ),
        )

        self.promo_kb = InlineKeyboardMarkup(row_width=2)
        self.promo_kb.add(
            InlineKeyboardButton(
                text="Создание промокода",
                callback_data="promo_create",
            ),
            InlineKeyboardButton(
                text="Список промокодов",
                callback_data="promo_list",
            ),
        )
        self.promo_kb.add(
            self.main_manu_button
        )
        self.promo_create_kb = InlineKeyboardMarkup(row_width=1)
        self.promo_create_kb.add(
            InlineKeyboardButton(
                text="Отменить создание",
                callback_data="promo_cancel",
            ),
            self.main_manu_button
        )

        self.promo_accept_kb = InlineKeyboardMarkup(row_width=1)
        self.promo_accept_kb.add(
            InlineKeyboardButton(
                "Подтвердить",
                callback_data="promo_insert",
            ),
            self.main_manu_button,
        )
        self.promo_generate_kb = InlineKeyboardMarkup(row_width=2)
        self.promo_generate_kb.add(
            InlineKeyboardButton(
                text="Ввести промокод вручную",
                callback_data="promo_manual",
            ),
            InlineKeyboardButton(
               text="Подтвердить",
               callback_data="promo_auto",
            ),
        )
        self.faq_kb = InlineKeyboardMarkup(row_width=1)
        self.faq_kb.add(
            self.main_manu_button
        )

        self.users_orders_kb = InlineKeyboardMarkup(row_width=2)
        self.users_orders_kb.add(
            InlineKeyboardButton(
                text="Меню пользователей",
                callback_data="users_menu",
            ),
            InlineKeyboardButton(
                text="Меню заказов",
                callback_data="orders_menu",
            ),
        )
        self.users_orders_kb.add(
            self.main_manu_button,
        )

        self.order_detail_kb = InlineKeyboardMarkup(row_with=2)
        self.order_detail_kb.add(
            InlineKeyboardButton(
                "Вернуться к листу заказов",
                callback_data="return_to_list",
            ),
        )
        self.order_detail_kb.add(
            InlineKeyboardButton(
                "Изменить артикул",
                callback_data="edit_art",
            ),
            InlineKeyboardButton(
                "Изменить ссылку на товар",
                callback_data="edit_http",
            ),
        )
        self.order_detail_kb.add(
            InlineKeyboardButton(
                "Изменить размер",
                callback_data="edit_menu_size",
            ),
            InlineKeyboardButton(
                "Изменить стоимость",
                callback_data="edit_menu_price",
            ),
        )
        self.order_detail_kb.add(
            InlineKeyboardButton(
                "Изменить доп. инфо",
                callback_data="edit_menu_addition",
            ),
            InlineKeyboardButton(
                "Изменить сумму к оплате",
                callback_data="edit_menu_pay",
            ),
        )
        self.order_detail_kb.add(
            InlineKeyboardButton(
                "Изменить количество потраченных баллов",
                callback_data="edit_points_spent",
            ),
            InlineKeyboardButton(
                "Изменить статус",
                callback_data="edit_status",
            ),
        )
        self.order_detail_kb.add(
            self.main_manu_button
        )
        self.order_edit_cancel = InlineKeyboardButton(
            "Отменить изменения",
            callback_data="cancel_order_changes",
        )
        self.order_change_stage1_kb = InlineKeyboardMarkup(row_width=1)
        self.order_change_stage1_kb.add(
            self.order_edit_cancel,
            self.main_manu_button,
        )
        self.order_change_stage2_kb = InlineKeyboardMarkup(row_width=1)
        self.order_change_stage2_kb.add(
            InlineKeyboardButton(
                "Подтвердить изменения",
                callback_data="confirm_changes",
            ),
            self.main_manu_button,
        )
        self.status_kb = InlineKeyboardMarkup(row_width=2)
        self.status_kb.add(
            self.order_edit_cancel,
        )
        self.status_kb.add(
            InlineKeyboardButton("Отменён", callback_data="edit_status_cancelled"),
            InlineKeyboardButton("В обработке", callback_data="edit_status_processing"),
        )
        self.status_kb.add(
            InlineKeyboardButton("Принят", callback_data="edit_status_accepted"),
            InlineKeyboardButton("В пути", callback_data="edit_status_in_transit"),
        )
        self.status_kb.add(
            InlineKeyboardButton("Готов к выдаче", callback_data="edit_status_ready_for_pickup"),
            self.main_manu_button,
        )
        self.text_to_user_kb = InlineKeyboardMarkup(row_width=2)
        self.text_to_user_kb.add(
            self.order_edit_cancel,
        )
        self.text_to_user_kb.add(
            InlineKeyboardButton(
                "Добавить",
                callback_data="add_text_to_user",
            ),
            InlineKeyboardButton(
                "Пропустить",
                callback_data="skip_text_to_user",
            )
        )
        self.text_to_user_kb.add(
            self.main_manu_button,
        )

        self.user_detail_kb = InlineKeyboardMarkup(row_with=2)
        self.user_detail_kb.add(
            InlineKeyboardButton(
                "Вернуться к листу пользователей",
                callback_data="return_to_user_list",
            ),
        )
        self.user_detail_kb.add(
            InlineKeyboardButton(
                "Просмотр заказов",
                callback_data="orders_menu",
            ),
            InlineKeyboardButton(
                "Изменение имени",
                callback_data="edit_name",
            ),
        )
        self.user_detail_kb.add(
            InlineKeyboardButton(
                "Удаление пользователя",
                callback_data="delete_user",
            ),
        )
        self.user_detail_kb.add(
            self.main_manu_button,
        )

        # Первый этап
        self.user_change_stage1_kb = InlineKeyboardMarkup(row_width=1)
        self.user_change_stage1_kb.add(
            InlineKeyboardButton(
                "Отменить изменения",
                callback_data="cancel_user_changes",
            ),
            self.main_manu_button,
        )
        # Второй этап
        self.user_change_stage2_kb = InlineKeyboardMarkup(row_width=1)
        self.user_change_stage2_kb.add(
            InlineKeyboardButton(
                "Подтвердить изменения",
                callback_data="confirm_user_changes",
            ),
            self.main_manu_button,
        )

        self.user_default_kb = InlineKeyboardMarkup(row_width=1)
        self.user_default_kb.add(
            InlineKeyboardButton(
                "Вернуться в профиль",
                callback_data="return_to_user_profile",
            ),
            self.main_manu_button,
        )

    async def get_user_default_kb(self):
        return self.user_default_kb

    async def get_user_delete_confirm(self):
        self.user_default_kb.add(
            InlineKeyboardButton(
                "Подтвердить",
                callback_data="delete_user_confirm",
            )
        )
        return self.user_default_kb

    async def get_user_change_stage1_kb(self):
        return self.user_change_stage1_kb

    async def get_user_change_stage2_kb(self):
        return self.user_change_stage2_kb

    def get_comission_course_kb(self):
        return self.comission_course_kb

    def get_back_kb(self):
        return self.back_kb

    def get_accept_card_kb(self):
        return self.accept_card_kb

    def get_promo_kb(self):
        return self.promo_kb

    def get_promo_create_kb(self):
        return self.promo_create_kb

    def get_promo_accept_kb(self):
        return self.promo_accept_kb

    async def get_order_detail_kb(self):
        return self.order_detail_kb

    async def get_order_stage1_kb(self):
        return self.order_change_stage1_kb

    async def get_order_change_stage2_kb(self):
        return self.order_change_stage2_kb

    async def get_status_kb(self):
        return self.status_kb

    async def get_text_to_user_kb(self):
        return self.text_to_user_kb

    async def get_user_detail_kb(self):
        return self.user_detail_kb

    def get_promo_list_kb(self, current_page):
        keyboard = InlineKeyboardMarkup(row_width=2)
        total_pages = db.get_promo_count()

        cancel_promo = InlineKeyboardButton(
            "Вернуться к управлению",
            callback_data="return drive",
        )

        keyboard.add(cancel_promo)

        prev_page_btn = None
        next_page_btn = None

        if current_page > 1:
            prev_page_btn = InlineKeyboardButton("<<", callback_data=f"promo_pg#{current_page-1}")
        if current_page < total_pages:
            next_page_btn = InlineKeyboardButton(">>", callback_data=f"promo_pg#{current_page+1}")

        if prev_page_btn and next_page_btn:
            keyboard.add(prev_page_btn, next_page_btn)
        elif prev_page_btn:
            keyboard.add(prev_page_btn)
        elif next_page_btn:
            keyboard.add(next_page_btn)

        keyboard.add(self.main_manu_button)

        return keyboard

    async def get_orders_list_kb(self, current_page):

        keyboard = InlineKeyboardMarkup(row_width=2)
        total_pages = await db.get_orders_admin_count()

        cancel_order_users = InlineKeyboardButton(
            "Вернуться к выбору меню",
            callback_data="return_to_main",
        )   

        keyboard.add(cancel_order_users)

        prev_page_btn = False
        next_page_btn = False

        if current_page > 1:
            prev_page_btn = InlineKeyboardButton("<<", callback_data=f"ord_pg#{current_page-1}")
        if current_page < total_pages:
            next_page_btn = InlineKeyboardButton(">>", callback_data=f"ord_pg#{current_page+1}")

        if prev_page_btn and next_page_btn:
            keyboard.add(prev_page_btn, next_page_btn)
        elif prev_page_btn:
            keyboard.add(prev_page_btn)
        elif next_page_btn:
            keyboard.add(next_page_btn)

        keyboard.add(self.main_manu_button)

        return keyboard

    async def get_user_list_kb(self, current_page):

        keyboard = InlineKeyboardMarkup(row_width=2)
        total_pages = await db.get_users_count()

        cancel_order_users = InlineKeyboardButton(
            "Вернуться к выбору меню",
            callback_data="return_to_main",
        )

        keyboard.add(cancel_order_users)

        prev_page_btn = False
        next_page_btn = False

        if current_page > 1:
            prev_page_btn = InlineKeyboardButton("<<", callback_data=f"usr_pg#{current_page-1}")
        if current_page < total_pages:
            next_page_btn = InlineKeyboardButton(">>", callback_data=f"usr_pg#{current_page+1}")

        if prev_page_btn and next_page_btn:
            keyboard.add(prev_page_btn, next_page_btn)
        elif prev_page_btn:
            keyboard.add(prev_page_btn)
        elif next_page_btn:
            keyboard.add(next_page_btn)

        keyboard.add(self.main_manu_button)

        return keyboard

    async def get_user_detail_orders_kb(self, current_page, user_id):
        keyboard = InlineKeyboardMarkup(row_width=2)
        total_pages = await db.get_user_detail_orders_count(user_id)

        cancel_order_users = InlineKeyboardButton(
            "Вернуться к выбору меню",
            callback_data="return_to_main",
        )   

        keyboard.add(cancel_order_users)

        prev_page_btn = False
        next_page_btn = False

        if current_page > 1:
            prev_page_btn = InlineKeyboardButton("<<", callback_data=f"usr_ord_pg#{current_page-1}")
        if current_page < total_pages:
            next_page_btn = InlineKeyboardButton(">>", callback_data=f"usr_ord_pg#{current_page+1}")

        if prev_page_btn and next_page_btn:
            keyboard.add(prev_page_btn, next_page_btn)
        elif prev_page_btn:
            keyboard.add(prev_page_btn)
        elif next_page_btn:
            keyboard.add(next_page_btn)

        keyboard.add(self.main_manu_button)

        return keyboard

    def get_promo_generate_kb(self):
        return self.promo_generate_kb

    def get_faq_kb(self):
        return self.faq_kb

    def get_users_orders_kb(self):
        return self.users_orders_kb
