import os
import aiohttp
import shutil

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ParseMode
from dotenv import load_dotenv

from database import sqlite_db
from validators import admin_validators as valid
from keyboards import (
    admin_kb as admn_kb,
    admin_inline_kb as admn_inl_kb,
    client_inline as cli,
)
from core import promo_creator as create, order_id_finder as oif


load_dotenv()
APP_ID = os.getenv("COURSE_KEY")

INLN_KB = admn_inl_kb.InlineAdminKeyboard()


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()


class FSMComissions(StatesGroup):
    comission_course = State()
    comission_course_change = State()
    insert_comission_change = State()
    insert_course_change = State()
    all_insert = State()
    actual_course = State()
    previous_state = State()


class FSMOrdersAndUsers(StatesGroup):
    order_menu = State()
    users_and_orders = State()
    order_detail = State()
    change_article = State()
    article_confirm = State()
    change_url = State()
    url_confirm = State()
    change_size = State()
    size_confirm = State()
    change_cost = State()
    cost_confirm = State()
    change_additional_info = State()
    additional_info_confirm = State()
    change_payment_amount = State()
    payment_amount_confirm = State()
    change_reward_points = State()
    reward_points_confirm = State()
    change_status = State()
    change_status_confirm = State()
    skip_message = State()
    message_insert = State()
    message_send = State()
    user_menu = State()
    user_detail = State()
    change_name = State()
    edit_name = State()
    confirm_user_changes = State()
    user_delete = State()
    send_requisites = State()
    confirm_req_send = State()
    req_send_to_user = State()
    ready_to_pick = State()
    ready_to_pick_confirm = State()
    ready_to_pick_mess = State()
    ready_to_pick_ins = State()
    ready_ok = State()


class FSMMoneyInfo(StatesGroup):
    change_requisites = State()
    accept_card = State()


class FSMOther(StatesGroup):
    promo_code = State()
    promo_code_start = State()
    apk_poizon = State()
    apk_accept = State()
    promo_code_value = State()
    promo_code_activation = State()
    promo_code_view = State()
    activation_error = State()
    promo_code_value_error = State()


class FSMContactAndFAQ(StatesGroup):
    contact_input = State()
    faq = State()
    faq_input = State()


async def insert_money_info_db(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if str(current_state) in str(FSMComissions.all_insert):
        valid_course, valid_comission = await valid.validate_course_commission(message.text)
        if valid_course:
            await message.answer("Значение курса валют и комиссии успешно обновлены!")
            await sqlite_db.insert_money_info(valid_course, valid_comission)
            await admin_menu(message, state)
        else:
            await message.answer("Значение курса валют и комиссии указаны неверно!")
            await admin_menu(message, state)
    else:
        validation = await valid.is_digit_validation(message.text)
        if validation:
            if str(current_state) in str(FSMComissions.insert_comission_change):
                await sqlite_db.update_comission(message.text)
                await message.reply("Комиссия успешно обновлена!")
                await admin_menu(message, state)
            else:
                await sqlite_db.update_course(message.text)
                await message.reply("Курс валюты успешно обновлен!")
                await admin_menu(message, state)
        else:
            await message.reply("Значение указанно неверно!")
            await admin_menu(message, state)


async def main_menu(callback: CallbackQuery, state: State):
    current_state = await state.get_state()
    if current_state is None:
        return None
    await state.finish()
    admin_kb = admn_kb.AdminMenuKeyboard()
    await callback.bot.send_message(
        callback.message.chat.id,
        text="&#127968;",
        reply_markup=admin_kb.get_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await callback.message.delete()


async def admin_menu(message: Message, state: FSMContext):

    user_id = message.chat.id
    admin = await sqlite_db.get_admin(user_id)

    if admin:
        admin_kb = admn_kb.AdminMenuKeyboard()
        await message.answer(
            f"Здравствуйте, дорогой администратор {admin[1]}!",
            reply_markup=admin_kb.get_keyboard()
        )
    else:
        await message.answer(
            "У вас нет прав администратора.",
            reply_markup=None
        )


# Функции меню админа
async def comission_change(message: Message, state: FSMContext):

    await message.answer(
        "Изменить комиссию и/или курс валюты?",
        reply_markup=INLN_KB.get_comission_course_kb()
    )
    await state.set_state(FSMComissions.comission_course)


async def insert_comission_change(callback: CallbackQuery, state: FSMContext):

    if callback.data.startswith("all"):

        await callback.message.edit_text(
            "Введите курс и комиссию в следующем формате:\n"
            "Курс: <цифровое значение>;  Комиссия: <цифровое значение>;\n\n"
            "*Цифровое значение может быть дробным.\n"
            "**Сообщения в любом другом формате не будут приняты!"
        )
        await state.set_state(FSMComissions.all_insert)

    elif "course" in callback.data:
        await callback.message.edit_text(
            "Введите только новое значение курса валют"
        )
        await state.set_state(FSMComissions.insert_course_change)

    else:
        await callback.message.edit_text(
            "Введите только новое значение комиссии"
        )
        await state.set_state(FSMComissions.insert_comission_change)


async def actual_course(callback: CallbackQuery, state: FSMContext):
    actual_course = await sqlite_db.get_money_info()
    CURRENCY_CNY = 'CNY' # код валюты юаня
    CURRENCY_RUB = 'RUB'

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://openexchangerates.org/api/latest.json?app_id={APP_ID}&symbols={CURRENCY_CNY}') as response_uan:
            async with session.get(f'https://openexchangerates.org/api/latest.json?app_id={APP_ID}&symbols={CURRENCY_RUB}') as response_rub:

                if response_uan.status == 200 and response_rub.status == 200:
                    data_uan = await response_uan.json()
                    data_rub = await response_rub.json()

                    rate_uan = data_uan['rates'][CURRENCY_CNY]
                    rate_rub = data_rub['rates'][CURRENCY_RUB]

                    if actual_course:
                        rate = round(rate_rub / rate_uan, 2)
                        await callback.message.edit_text(
                            f"Стабильный курс валюты: {actual_course[1]}\n"
                            f"Акутальный курс валюты рубля к юаню: {rate}",
                            reply_markup=INLN_KB.get_back_kb()
                        )
                        await state.set_state(FSMComissions.previous_state)
                    else:
                        await callback.message.edit_text(
                            "Курс валюты не задан."
                        )
                        await admin_menu(callback.message, state)
                else:
                    await callback.message.edit_text(
                        "Ошибка получения актуального курса валют."
                    )
                    await admin_menu(callback.message, state)


async def back(callback: CallbackQuery, state: FSMContext):
    current_state = str(await state.get_state())
    if current_state in str(FSMComissions.previous_state):
        await callback.message.edit_reply_markup(None)
        await comission_change(callback.message, state)


async def change_requisites(message: Message, state: FSMContext):
    await message.answer(
        "Введите номер карты для реквизита",
        reply_markup=INLN_KB.card_main
    )
    await state.set_state(FSMMoneyInfo.change_requisites)


async def accept_card(message: Message, state: FSMContext):
    validation = await valid.is_digit_validation(message.text)
    if validation and len(message.text) == 16:
        await message.answer(
            f"Подтвердить ввод карты: {message.text}?",
            reply_markup=INLN_KB.get_accept_card_kb()
        )
        await state.set_state(FSMMoneyInfo.accept_card)
    else:
        await message.answer(
            "Неверный ввод номера карты.",
        )
        await change_requisites(message, state)


async def cancel_card(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Реквизиты карты отменены."
    )
    await admin_menu(callback.message, state)


async def accept_card_yes(callback: CallbackQuery, state: FSMContext):
    await sqlite_db.change_requisites(callback.message.text)
    await callback.message.edit_text(
        "Реквизиты карты изменены."
    )
    await admin_menu(callback.message, state)


async def poizon_change_apk(message: Message, state: FSMContext):
    await message.answer("Отправьте новый APK файл")
    await state.set_state(FSMOther.apk_poizon)


async def apk_accept(message: Message, state: FSMContext):
    await message.answer_document(
        message.document.file_id,
        reply_markup=INLN_KB.poizon_load_kb
    )
    await state.set_state(FSMOther.apk_accept)


async def cancel_apk(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Загрузка APK файла отменена"
    )
    await admin_menu(callback.message, state)


async def accept_apk(callback: CallbackQuery, state: FSMContext):

    directory = 'poizon_apk/'

    try:
        shutil.rmtree(directory)
        print(f"Все файлы из {directory} удалены")
    except Exception as e:
        print(f"Ошибка при удалении файлов из {directory}: {e}")

    await callback.message.document.download(destination_dir=directory)

    await callback.message.answer("APK файл изменен")
    await admin_menu(callback.message, state)


async def promo_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Промокод отменен."
    )
    await promo_create(callback.message, state)


async def promo_list_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Возвращение к управлению промокодами"
    )
    await promo_create(callback.message, state)


async def promo_create(message: Message, state: FSMContext):
    await message.answer(
        "Выберите действие",
        reply_markup=INLN_KB.promo_kb
    )
    await state.set_state(FSMOther.promo_code)


async def promo_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите промокод",
        reply_markup=INLN_KB.get_promo_create_kb()
    )
    await state.set_state(FSMOther.promo_code_start)


async def promo_value(message: Message, state: FSMContext):

    current_state = await state.get_state()
    promo, valid = await sqlite_db.check_promo(message.text)
    error = False

    if str(current_state) in str(FSMOther.promo_code_value_error):
        error = True

    if not promo:
        if not error:
            async with state.proxy() as data:
                data["promo"] = message.text

        await message.answer(
            "Введите сумму промокода",
            reply_markup=INLN_KB.get_promo_create_kb()
        )
        await state.set_state(FSMOther.promo_code_value)
    else:

        promo = await create.generate_promo_code(5)
        await message.answer(
            "Введенный Вами промокод уже существует\n"
            f"Может подойдет {promo}?",
            reply_markup=INLN_KB.get_promo_generate_kb(),
        )
        async with state.proxy() as data:
            data["promo_generate"] = promo


async def promo_generate_accept(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Промокод был подтвержден!"
    )

    data = await state.get_data()
    promo = data.get("promo_generate")

    callback.message.text = promo
    await state.set_state(FSMOther.promo_code_start)
    await promo_value(callback.message, state)


async def promo_manual_create(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOther.promo_code)
    await promo_create_start(callback, state)


async def promo_activation_value(message: Message, state: FSMContext):

    current_state = await state.get_state()

    validation = await valid.is_digit_validation(message.text)
    if str(current_state) in str(FSMOther.activation_error):
        validation = True

    if validation:
        await state.set_state(FSMOther.promo_code_activation)

        if not str(current_state) in str(FSMOther.activation_error):
            async with state.proxy() as data:
                data["value"] = message.text

        await message.answer(
            "Введитие количество активаций",
            reply_markup=INLN_KB.get_promo_create_kb()
        )
    else:
        await message.answer(
            "Ввод некорректен.\n"
            "Сумма промокода должна быть в числовом формате."
        )
        await state.set_state(FSMOther.promo_code_value_error)
        await promo_value(message, state)


async def promo_view(message: Message, state: FSMContext):

    validation = await valid.is_digit_validation(message.text)

    if validation:
        async with state.proxy() as data:
            data["activation"] = message.text

        await state.set_state(FSMOther.promo_code_view)
        await message.answer(
            f"Промокод: {data['promo']}\n"
            f"Сумма: {data['value']}\n"
            f"Количество активаций: {data['activation']}",
            reply_markup=INLN_KB.get_promo_accept_kb()
        )

    else:
        await message.answer(
            "Ввод некорректен.\n"
            "Количество активаций должно быть в числовом формате."
        )
        await state.set_state(FSMOther.activation_error)
        await promo_activation_value(message, state)


async def insert_promo_db(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Промокод успешно создан!"
    )

    async with state.proxy() as data:
        await sqlite_db.insert_promo(data)

    await promo_create(callback.message, state)


async def promo_list(callback: CallbackQuery, state: FSMContext):
    page_number = int(callback.data.split("#")[1]) if "#" in callback.data else 1
    await callback.message.edit_text(
        text=await sqlite_db.get_promo_list(callback.message, page_number),
        reply_markup=INLN_KB.get_promo_list_kb(page_number)
    )


async def faq_section(messsge: Message, state: FSMContext):
    await messsge.answer(
        text="Введите информацию в следующем формате:\n"
             "?<Вопрос> !<Ответ>;\n\n"
             "*Любой другой формат не будет принят.\n"
             "**Комбинаций ?вопрос !ответ; может быть любое количество.\n"
             "***Каждая комбинация ?вопрос !ответ должен быть разделен знаком ';'",
             reply_markup=INLN_KB.get_faq_kb()
    )
    await state.set_state(FSMContactAndFAQ.faq)


async def faq_input(message: Message, state: FSMContext):

    faq = await valid.validate_faq(message.text)

    if faq:
        await sqlite_db.sql_insert_faq(faq)
        await message.answer(
            text="Все FAQ были успешно добавлены!",
            reply_markup=INLN_KB.get_faq_kb()
        )
        await state.set_state(FSMContactAndFAQ.faq_input)
    else:
        await message.answer(
            text="Формат ввода не соответствует формату"
        )
        await faq_section(message, state)


async def contact_change(message: Message, state: FSMContext):
    await message.answer(
        text="Введите контакт для Telegram",
        reply_markup=INLN_KB.get_faq_kb()
    )
    await state.set_state(FSMContactAndFAQ.contact_input)


async def contact_insert_db(message: Message, state: FSMContext):
    await sqlite_db.update_admin_record(admin_id=message.from_user.id, tg_link=message.text)
    await message.answer(
        text="Контактные данные успешно обновлены!",
        reply_markup=INLN_KB.get_faq_kb()
    )


async def return_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Вы вернулись в меню",
    )
    await users_and_orders(callback.message, state)


async def users_and_orders(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.users_and_orders)
    await message.answer(
        text="Вы можете открыть меню просмотра пользователей и заказов",
        reply_markup=INLN_KB.get_users_orders_kb()
    )


async def return_to_list(callback: CallbackQuery, state: FSMContext):
    await order_menu(callback, state)


async def order_menu(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    page_number = int(callback.data.split("#")[1]) if "#" in callback.data else 1

    if str(current_state) in str(FSMOrdersAndUsers.user_detail):

        data = await state.get_data()
        user_id = data["user_id"]

        text = await sqlite_db.get_user_detail_orders(
            user_id,
            page_number,
        )
        keyboard = await INLN_KB.get_user_detail_orders_kb(
            page_number,
            user_id,
        )
    else:
        text = await sqlite_db.get_orders_for_admin(
            callback.message,
            page_number,
        )
        keyboard = await INLN_KB.get_orders_list_kb(page_number)
        await state.set_state(FSMOrdersAndUsers.order_menu)

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


async def confirm_changes(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    async with state.proxy() as data:
        await sqlite_db.sql_add_order(data["order_edit_data"], edit=True)

    print(current_state)

    if str(current_state) in str(FSMOrdersAndUsers.ready_to_pick_confirm):
        print("here")
        return await send_requisites(callback, state)

    callback.message.text = data["order_edit_data"][0]
    await state.set_state(FSMOrdersAndUsers.order_menu)
    await order_detail(callback.message, state)
    await callback.message.delete()


async def cancel_changes(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    order_id = data["order_data"][0]
    callback.message.text = order_id

    await state.set_state(FSMOrdersAndUsers.order_menu)
    await order_detail(callback.message, state)
    await callback.message.delete()


async def order_detail(message: Message, state=FSMContext):

    current_state = await state.get_state()

    if str(current_state) in (
        str(FSMOrdersAndUsers.order_menu)
    ) or str(current_state) in (
        str(FSMOrdersAndUsers.user_detail)
    ):

        order = await sqlite_db.get_order_detail(message.text)
        if order:
            user = await sqlite_db.sql_check_user("user_id", order[11])
    else:
        order = True

    if order:

        print(str(current_state) in str(FSMOrdersAndUsers.order_menu))
        if str(current_state) not in (
            str(FSMOrdersAndUsers.order_menu)
        ) and str(current_state) not in (
            str(FSMOrdersAndUsers.user_detail)
        ):
            data = await state.get_data()
            order = data["order_edit_data"]
            user = data["user_data"]

        msg = (
            f'\n\nНомер заказа: {order[0]}\n'
            f'Артикул: {order[1]}\n'
            f'Ссылка на товар: {order[2]}\n'
            f'Размер: {order[3]}\n'
            f'Стоимость: {order[4]}\n'
            f'Стоимость к оплате: {order[6]}\n'
            f'Дата заказа: {order[8]}\n'
            f'Количество потраченных баллов: {order[9]}\n'
            f'Статус: {order[10]}\n'
            f'Пользователь: {user[9]}\n'
            f'Номер аккаунта: {user[0]}\n'
        )
        if order[5] or order[13]:
            msg += 'Доп. инфо: Прикреплено'
        else:
            msg += 'Доп инфо: Отсутствует'

        if str(current_state) in (
            str(FSMOrdersAndUsers.order_menu)
        ) or str(current_state) in (
            str(FSMOrdersAndUsers.user_detail)
        ):
            async with state.proxy() as data:
                data["order_data"] = order
                data["user_data"] = user
            keyboard = await INLN_KB.get_order_detail_kb()
            await state.set_state(FSMOrdersAndUsers.order_detail)
        else:
            keyboard = await INLN_KB.get_order_change_stage2_kb()

        await message.answer(
            text=msg,
            reply_markup=keyboard
        )

    else:

        await message.answer(
            "Заказа с таким номером не существует.\n"
            "Пришлите номер существующего заказа!"
        )
        await users_and_orders(message, state)


async def change_article(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_article)
    await callback.message.edit_text(
        "Введите артикул",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def article_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.article_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:1] + (message.text,) + order_data[2:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_url)
    await callback.message.edit_text(
        "Введите ссылки на товар",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def url_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.url_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:2] + (message.text,) + order_data[3:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_size(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_size)
    await callback.message.edit_text(
        "Введите размер",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def size_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.size_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:3] + (message.text,) + order_data[4:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_cost(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_cost)
    await callback.message.edit_text(
        "Введите стоимость",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def cost_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.cost_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:4] + (message.text,) + order_data[5:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_additional_info(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    await state.set_state(FSMOrdersAndUsers.change_additional_info)

    if not data["order_data"][13] or not data["order_data"][5]:
        await callback.message.edit_text(
            "Введите дополнительную информацию",
            reply_markup=await INLN_KB.get_order_stage1_kb()
        )
    if data["order_data"][5] and not data["order_data"][13]:
        await callback.message.edit_text(
            f"Доп. информация заказа: {data['order_data'][5]}\n\n"
            "Введите дополнительную информацию",
            reply_markup=await INLN_KB.get_order_stage1_kb()
        )
    else:
        capt = (
            f"Доп. информация заказа: {data['order_data'][5]}\n\n"
            "Введите дополнительную информацию"
        )
        await callback.message.answer_photo(
            photo=data["order_data"][13],
            caption=capt,
            reply_markup=await INLN_KB.get_order_stage1_kb(),
        )


async def additional_info_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.additional_info_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:5] + (message.text,) + order_data[6:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_payment_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_payment_amount)
    await callback.message.edit_text(
        "Введите сумму к оплате",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def payment_amount_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.payment_amount_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:6] + (message.text,) + order_data[7:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_reward_points(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_reward_points)
    await callback.message.edit_text(
        "Введите количество потраченных баллов",
        reply_markup=await INLN_KB.get_order_stage1_kb()
    )


async def reward_points_confirm(message: Message, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.reward_points_confirm)
    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:9] + (message.text,) + order_data[10:]
        data["order_edit_data"] = order_data

    await order_detail(message, state)


async def change_status(callback: CallbackQuery, state: FSMContext):
    status_map = {
        "edit_status_cancelled": "Отменён",
        "edit_status_processing": "В обработке",
        "edit_status_accepted": "Принят",
        "edit_status_in_transit": "В пути",
        "edit_status_ready_for_pickup": "Готов к выдаче"
    }
    async with state.proxy() as data:
        data["status_map"] = status_map

    await state.set_state(FSMOrdersAndUsers.change_status)
    await callback.message.edit_text(
        "Выберите новый статус",
        reply_markup=await INLN_KB.get_status_kb()
    )


async def change_status_confirm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_status_confirm)
    async with state.proxy() as data:
        data["status"] = callback.data

    status_map = data["status_map"]
    status = status_map.get(data["status"])

    await callback.message.edit_text(
        f"Выбранный статус: {status}.\n"
        "Хотите добавить сообщение для пользователя?",
        reply_markup=await INLN_KB.get_text_to_user_kb(),
    )

    if status == "Готов к выдаче":
        await state.set_state(FSMOrdersAndUsers.ready_to_pick)


async def skip_message(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    admin = await sqlite_db.get_admin(callback.message.chat.id)
    admin_contact = admin[3]

    data = await state.get_data()
    status_map = data["status_map"]
    user = data["user_data"]
    order = data["order_data"]
    status = status_map.get(data["status"])

    msg = (
        f"Здравствуйте, {user[9]}! Ваш заказ под номером {order[0]} {status}."
        f"Контакт службы поддержки: @{admin_contact}"
    )
    await callback.message.bot.send_message(user[1], msg)

    await callback.message.edit_text(
        "Сообщение отправлено пользователю!",
    )

    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:10] + (status,) + order_data[11:]
        data["order_edit_data"] = order_data
    callback.message.text = data["order_data"][0]


    if str(current_state) in str(FSMOrdersAndUsers.ready_to_pick):
        await state.set_state(FSMOrdersAndUsers.ready_to_pick_confirm)
    else:
        await state.set_state(FSMOrdersAndUsers.skip_message)

    await order_detail(callback.message, state)


async def message_insert(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()
    if str(current_state) in str(FSMOrdersAndUsers.ready_to_pick):
        await state.set_state(FSMOrdersAndUsers.ready_to_pick_ins)
    else:
        await state.set_state(FSMOrdersAndUsers.message_insert)

    await callback.message.edit_text(
        "Введите сообщение",
        reply_markup=await INLN_KB.get_text_to_user_kb(),
    )


async def message_send(message: Message, state: FSMContext):

    current_state = await state.get_state()

    data = await state.get_data()
    status_map = data["status_map"]
    status = status_map.get(data["status"])
    user = data["user_data"]

    if not message.photo:
        await message.bot.send_message(user[1], message.text)

    else:
        await message.bot.send_photo(user[0], message.photo[-1].file_id, caption=message.text)

    await message.answer("Сообщение отправлено пользователю!")

    async with state.proxy() as data:
        order_data = data.get("order_data", ())
        order_data = order_data[:10] + (status,) + order_data[11:]
        data["order_edit_data"] = order_data

    if str(current_state) in str(FSMOrdersAndUsers.ready_to_pick_ins):
        await state.set_state(FSMOrdersAndUsers.ready_to_pick_confirm)
    else:
        await state.set_state(FSMOrdersAndUsers.message_send)
    await order_detail(message, state)


async def send_requisites(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    data = await state.get_data()
    user_data = data["user_data"]
    order_data = data["order_data"]
    money_info = await sqlite_db.get_money_info()
    async with state.proxy() as data:
        data["money_info"] = money_info

    await callback.message.edit_text(
        f"Отправить реквизиты пользователю {user_data[9]}\n"
        f"Заказ: {order_data[0]}\n"
        f"Данные раздела оплаты: {money_info[3]}",
        reply_markup=await INLN_KB.get_send_req_kb(),
    )

    if str(current_state) in str(FSMOrdersAndUsers.order_detail):
        await state.set_state(FSMOrdersAndUsers.confirm_req_send)
    else:
        await state.set_state(FSMOrdersAndUsers.ready_ok)


async def confirm_req_send(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "Реквизиты отправлены пользователю!",
    )

    data = await state.get_data()
    order_id = data["order_data"][0]
    callback.message.text = order_id
    await state.set_state(FSMOrdersAndUsers.order_menu)
    await order_detail(callback.message, state)


async def req_send_to_user(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    data = await state.get_data()
    requisites = data["money_info"][3]
    order_id = data["order_data"][0]
    user_id = data["user_data"][1]

    if str(current_state) in str(FSMOrdersAndUsers.confirm_req_send):

        msg = (
            f"Реквизиты для оплаты:\n"
            f"Номер карты: {requisites}\n"
            f"Комментарий к переводу: byhedzy-{order_id}"
        )

    else:
        msg = (
            f"Один из Ваших заказов готов к выдаче!\n\n"
            f"Реквизиты для оплаты доставки:\n"
            f"Номер карты: {requisites}\n"
            f"Комментарий к переводу: byhedzy-{order_id}"
        )

    await callback.message.bot.send_message(
        user_id,
        text=msg,
        reply_markup=cli.pay_for_order_kb,
    )
    await state.set_state(FSMOrdersAndUsers.req_send_to_user)
    await confirm_req_send(callback, state)


async def user_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.user_menu)
    page_number = int(callback.data.split("#")[1]) if "#" in callback.data else 1
    await callback.message.edit_text(
        text=await sqlite_db.get_user_list(
            callback.message,
            page_number,
        ),
        reply_markup=await INLN_KB.get_user_list_kb(page_number),
    )


async def users_detail(message: Message, state: FSMContext):

    user = True
    current_state = await state.get_state()

    if str(current_state) in str(FSMOrdersAndUsers.user_menu):
        user = await sqlite_db.sql_check_user("id", message.text)

    if user:

        if str(current_state) not in str(FSMOrdersAndUsers.user_menu):
            data = await state.get_data()
            user = data.get("user_edit_data", ())

        if str(current_state) in str(FSMOrdersAndUsers.user_menu):
            async with state.proxy() as data:
                data["user_data"] = user
                data["user_id"] = user[0]

            keyboard = await INLN_KB.get_user_detail_kb()
            await state.set_state(FSMOrdersAndUsers.user_detail)

        else:
            keyboard = await INLN_KB.get_user_change_stage2_kb()
            await state.set_state(FSMOrdersAndUsers.confirm_user_changes)

        msg = (
            f'\n\nПользователь: {user[9]}\n'
            f'Количество BYN баллов: {user[3]}\n'
            f'Количество заказов: {user[2]}\n'
            f'Дата послед. заказа: {user[8]}\n'
            f'Номер аккаунта: {user[0]}\n'
        )

        await message.answer(
            text=msg,
            reply_markup=keyboard
        )

    else:

        await message.answer(
            "Пользователя с таким номером или ником не существует.\n"
            "Пришлите номер или ник существующего пользователя!"
        )
        await users_and_orders(message, state)


async def return_to_users_list(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.user_menu)
    await user_menu(callback, state)


async def return_to_user_profile(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.user_menu)
    await users_detail(callback.message, state)


async def change_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrdersAndUsers.change_name)
    await callback.message.edit_text(
        "Введите новое имя пользователя",
        reply_markup=await INLN_KB.get_user_default_kb(),
    )


async def edit_profile_name(message: Message, state: FSMContext):
    new_name = message.text
    if await sqlite_db.sql_check_user("username", new_name):

        data = await state.get_data()

        await message.answer(
            "Такой никнейм уже занят.",
        )
        await state.set_state(FSMOrdersAndUsers.user_menu)
        message.text = data["user_id"]
        await users_detail(message, state)

    else:
        await state.set_state(FSMOrdersAndUsers.edit_name)
        async with state.proxy() as data:
            user_data = data.get("user_data", ())
            user_data = user_data[:9] + (new_name,) + user_data[10:]
            data["user_edit_data"] = user_data
        message.text = data["user_id"]
        await users_detail(message, state)


async def confirm_user_changes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_data = data.get("user_edit_data", ())
    await sqlite_db.update_user(user_data)

    callback.message.text = data["user_id"]
    await state.set_state(FSMOrdersAndUsers.user_menu)
    await users_detail(callback.message, state)
    await callback.message.delete()


async def confirm_delete_user(callback: CallbackQuery, state: FSMContext):

    await state.set_state(FSMOrdersAndUsers.user_delete)
    data = await state.get_data()
    user_name = data["user_data"][9]
    await callback.message.edit_text(
        f"Вы уверены что хотите удалить пользователя {user_name}?",
        reply_markup=await INLN_KB.get_user_delete_confirm(),
    )


async def delete_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_data = data.get("user_data", ())
    await sqlite_db.delete_user(user_data[1])

    callback.message.text = data["user_id"]
    await state.set_state(FSMOrdersAndUsers.users_and_orders)
    await user_menu(callback, state)
    await callback.message.answer("Пользователь успешно удален!")


async def pay_check_ok(callback: CallbackQuery, state: FSMContext):

    order_id, user_id = await oif.find_user_id(callback.message.text)

    await callback.message.edit_text(
        "Сообщение отправлено!"
    )

    msg = (
        f"Оплата за заказ под номером {order_id} успешно подтверждена!\n"
        "Ожидайте доставки товара!"
    )

    await callback.message.bot.send_message(
        user_id,
        text=msg,
    )


async def pay_check_fail(callback: CallbackQuery, state: FSMContext):

    order_id, user_id = await oif.find_user_id(callback.message.text)

    await callback.message.edit_text(
        "Сообщение отправлено!"
    )

    msg = (
        f"Оплата за заказ под номером {order_id} не прошла!\n"
        "Свяжитесь со службой поддержки в разделе 'Служба поддержки'."
    )

    await callback.message.bot.send_message(
        user_id,
        text=msg,
    )


def register_handlers_admin(dp):

    dp.register_message_handler(
        insert_money_info_db,
        lambda message: "Курс:" in message.text or message.text.isdigit(),
        state=[FSMComissions.all_insert, FSMComissions.insert_course_change, FSMComissions.insert_comission_change]
    )
    dp.register_callback_query_handler(main_menu, lambda callback: callback.data == "main_menu", state="*")
    dp.register_message_handler(admin_menu, commands=['admin_bot'], state="*")
    dp.register_message_handler(comission_change, lambda message: "Изменить комиссию и/или курс валют" in message.text, state="*")
    dp.register_callback_query_handler(insert_comission_change, lambda callback: "change" in callback.data, state=FSMComissions.comission_course)

    dp.register_callback_query_handler(actual_course, lambda callback: callback.data == "check_uan", state=FSMComissions.comission_course)
    dp.register_callback_query_handler(back, lambda callback: callback.data == "back", state=FSMComissions.previous_state)

    dp.register_message_handler(change_requisites, lambda message: "реквизитов" in message.text, state="*")
    dp.register_message_handler(accept_card, state=FSMMoneyInfo.change_requisites)
    dp.register_callback_query_handler(accept_card_yes, lambda callback: callback.data == "accept_card", state=FSMMoneyInfo.accept_card)
    dp.register_callback_query_handler(cancel_card, lambda callback: callback.data == "cancel_card", state=FSMMoneyInfo.accept_card)
    dp.register_message_handler(poizon_change_apk, lambda message: "Изменение APK" in message.text, state="*")
    dp.register_message_handler(apk_accept, content_types=['document'], state=FSMOther.apk_poizon)
    dp.register_callback_query_handler(cancel_apk, lambda callback: callback.data == "cancel_apk", state=FSMOther.apk_accept)
    dp.register_callback_query_handler(accept_apk, lambda callback: callback.data == "accept_apk", state=FSMOther.apk_accept)

    dp.register_message_handler(promo_create, lambda message: "Создание промокодов" in message.text, state="*")
    dp.register_callback_query_handler(promo_create_start, lambda callback: callback.data == "promo_create", state=FSMOther.promo_code)
    dp.register_message_handler(promo_value, state=FSMOther.promo_code_start)
    dp.register_message_handler(promo_activation_value, state=[FSMOther.promo_code_value, FSMOther.activation_error])
    dp.register_message_handler(promo_view, state=FSMOther.promo_code_activation)
    dp.register_callback_query_handler(promo_cancel, lambda callback: callback.data == "promo_cancel", state="*")
    dp.register_callback_query_handler(insert_promo_db, lambda callback: callback.data == "promo_insert", state=FSMOther.promo_code_view)
    dp.register_callback_query_handler(promo_list, lambda callback: "promo_list" in callback.data or (callback.data.startswith("promo_pg#")), state=FSMOther.promo_code)
    dp.register_callback_query_handler(promo_list_cancel, lambda callback: "return drive" in callback.data, state="*")
    dp.register_callback_query_handler(promo_generate_accept, lambda callback: "promo_auto" in callback.data, state=FSMOther.promo_code_start)
    dp.register_callback_query_handler(promo_manual_create, lambda callback: "promo_manual" in callback.data, state=FSMOther.promo_code_start)
    dp.register_message_handler(faq_section, lambda message: "Изменение информации" in message.text, state="*")
    dp.register_message_handler(faq_input, state=FSMContactAndFAQ.faq)
    dp.register_message_handler(contact_change, lambda message: "Изменение контактов" in message.text, state="*")
    dp.register_message_handler(contact_insert_db, state=FSMContactAndFAQ.contact_input)
    dp.register_message_handler(users_and_orders, lambda message: "Просмотр пользователей и заказов" in message.text, state="*")
    dp.register_callback_query_handler(
        order_menu,
        lambda callback: callback.data == "orders_menu" or (

            callback.data.startswith("ord_pg#")
            or callback.data.startswith("usr_ord_pg#")
        ),
        state=[
            FSMOrdersAndUsers.users_and_orders,
            FSMOrdersAndUsers.order_menu,
            FSMOrdersAndUsers.user_detail,
        ],
    )
    dp.register_callback_query_handler(return_to_menu, lambda callback: callback.data == "return_to_main", state=[FSMOrdersAndUsers.order_menu, FSMOrdersAndUsers.user_detail, FSMOrdersAndUsers.user_menu])
    dp.register_callback_query_handler(change_article, lambda callback: "edit_art" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(article_confirm, state=FSMOrdersAndUsers.change_article)
    dp.register_callback_query_handler(confirm_changes, lambda callback: "confirm_changes" in callback.data, state="*")
    dp.register_callback_query_handler(change_url, lambda callback: "edit_http" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(url_confirm, state=FSMOrdersAndUsers.change_url)
    dp.register_callback_query_handler(return_to_list, lambda callback: "return_to_list" in callback.data, state=FSMOrdersAndUsers.order_detail)

    # Хендлеры для функций изменения размера
    dp.register_callback_query_handler(change_size, lambda callback: "edit_menu_size" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(size_confirm, state=FSMOrdersAndUsers.change_size)

    # Хендлеры для функций изменения стоимости
    dp.register_callback_query_handler(change_cost, lambda callback: "edit_menu_price" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(cost_confirm, state=FSMOrdersAndUsers.change_cost)

    # Хендлеры для функций изменения дополнительной информации
    dp.register_callback_query_handler(change_additional_info, lambda callback: "edit_menu_addition" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(additional_info_confirm, state=FSMOrdersAndUsers.change_additional_info)

    # Хендлеры для функций изменения суммы к оплате
    dp.register_callback_query_handler(change_payment_amount, lambda callback: "edit_menu_pay" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(payment_amount_confirm, state=FSMOrdersAndUsers.change_payment_amount)

    # Хендлеры для функций изменения количества потраченных баллов
    dp.register_callback_query_handler(change_reward_points, lambda callback: "edit_points_spent" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_message_handler(reward_points_confirm, state=FSMOrdersAndUsers.change_reward_points)
    dp.register_callback_query_handler(cancel_changes, lambda callback: "cancel_order_changes" in callback.data, state="*")

    # Хендлеры для функции изменения статуса
    dp.register_callback_query_handler(change_status, lambda callback: "edit_status" in callback.data, state=FSMOrdersAndUsers.order_detail)
    dp.register_callback_query_handler(change_status_confirm, lambda callback: callback.data.startswith("edit_status_"), state=FSMOrdersAndUsers.change_status)

    # Хендлеры для функции пропуска отправки сообщения
    dp.register_callback_query_handler(skip_message, lambda callback: "skip_text_to_user" in callback.data, state=[FSMOrdersAndUsers.change_status_confirm, FSMOrdersAndUsers.ready_to_pick])

    # Хендлеры для функции ввода сообщения
    dp.register_callback_query_handler(message_insert, lambda callback: "add_text_to_user" in callback.data, state=[FSMOrdersAndUsers.change_status_confirm, FSMOrdersAndUsers.ready_to_pick])

    # Хендлеры для функции отправки сообщения
    dp.register_message_handler(message_send, state=[FSMOrdersAndUsers.message_insert, FSMOrdersAndUsers.ready_to_pick_ins])

    dp.register_message_handler(
        order_detail,
        lambda message: message.text.isdigit(),
        state=(
            FSMOrdersAndUsers.user_detail,
            FSMOrdersAndUsers.order_menu,
            FSMOrdersAndUsers.article_confirm,
        )
    )

    dp.register_callback_query_handler(user_menu, lambda callback: "users_menu" in callback.data or callback.data.startswith("usr_pg#"), state=[FSMOrdersAndUsers.users_and_orders, FSMOrdersAndUsers.user_menu, FSMOrdersAndUsers.user_detail])
    dp.register_message_handler(users_detail, state=FSMOrdersAndUsers.user_menu)
    dp.register_callback_query_handler(return_to_users_list, lambda callback: "return_to_user_list" in callback.data, state=FSMOrdersAndUsers.user_detail)
    dp.register_callback_query_handler(return_to_user_profile, lambda callback: "return_to_user_profile" in callback.data, state=FSMOrdersAndUsers.change_name)
    dp.register_callback_query_handler(change_name, lambda callback: "edit_name" in callback.data, state=FSMOrdersAndUsers.user_detail)
    dp.register_message_handler(edit_profile_name, state=FSMOrdersAndUsers.change_name)
    dp.register_callback_query_handler(confirm_user_changes, lambda callback: "confirm_user_changes" in callback.data, state=FSMOrdersAndUsers.confirm_user_changes)
    dp.register_callback_query_handler(confirm_delete_user, lambda callback: "delete_user" in callback.data, state=FSMOrdersAndUsers.user_detail)
    dp.register_callback_query_handler(delete_user, lambda callback: "delete_user_confirm" in callback.data, state=FSMOrdersAndUsers.user_delete)
    dp.register_callback_query_handler(send_requisites, lambda callback: "req_send" in callback.data, state=[FSMOrdersAndUsers.order_detail, FSMOrdersAndUsers.ready_to_pick, FSMOrdersAndUsers.ready_to_pick_confirm])
    dp.register_callback_query_handler(req_send_to_user, lambda callback: "confirm_req_send" in callback.data, state=[FSMOrdersAndUsers.confirm_req_send, FSMOrdersAndUsers.ready_to_pick, FSMOrdersAndUsers.ready_ok])
    dp.register_callback_query_handler(pay_check_ok, lambda callback: "payment_ok" in callback.data, state="*")
    dp.register_callback_query_handler(pay_check_fail, lambda callback: "payment_fail" in callback.data, state="*")
