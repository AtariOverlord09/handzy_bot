'''*****************************КЛИЕНТСКАЯ ЧАСТЬ****************************'''
from datetime import datetime
from typing import Union

from aiogram.types import Message, ParseMode, CallbackQuery, InputFile
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards import client_kb as kb, client_inline as kbl
from database import sqlite_db
from validators import client_validators as valid
from core import message_for_admins as msa, order_id_finder as oif


class FSMClient(StatesGroup):
    start = State()

    profile_view = State()

    waiting_for_product = State()
    waiting_for_size = State()
    waiting_for_price = State()
    waiting_for_addition = State()
    waiting_for_edit = State()
    waiting_for_approve = State()

    waiting_for_name = State()
    orders_view = State()
    actual_course = State()
    promo_activation = State()
    pozion_install = State()
    sync_accounts = State()
    support = State()
    answer_to_question = State()

    edit_url = State()
    edit_size = State()
    edit_price = State()
    edit_addition = State()
    edit_done = State()
    edit_url_done = State()
    edit_price_done = State()
    edit_size_done = State()
    edit_addition_done = State()
    edit_all_done = State()

    data_validate = State()
    url_validate = State()
    price_validate = State()

    cancel_order_to_eblan = State()
    eblan_pay_order = State()


class FSMPayment(StatesGroup):
    payment = State()
    waiting_for_confirmation = State()
    waiting_for_result = State()
    use_points = State()


async def command_start(message: Message, state: FSMContext):
    await message.reply(
        f"Здравствуйте, {message.from_user.full_name}! \n"
        "Я ваш бот для заказов.\nПожалуйста, ознакомьтесь с разделом "
        "<a href='ссылка на статью отдельная для вк и тг'>вопрос-ответ</a>. \n"
        "Приятных заказов!",
        reply_markup=kb.client_keyboard,
        parse_mode=ParseMode.HTML,
    )
    user = await sqlite_db.sql_check_user("user_id", message.from_user.id)
    if not user:
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['username'] = message.from_user.username
            data['orders_count'] = 0
            data['points'] = 0
            data['promo_codes'] = ''
            data['vk_link'] = ''
            data['tg_link'] = message.from_user.username
            data['registration_date'] = str(datetime.now())
            data['last_order_date'] = ''
            await sqlite_db.sql_add_user(data)

    await state.set_state(FSMClient.start)


async def cancel_order(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return None
    await state.finish()
    await callback.bot.send_message(
        callback.message.chat.id,
        text="&#127968;",
        reply_markup=kb.client_keyboard,
        parse_mode=ParseMode.HTML,
    )
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(FSMClient.start)


async def make_order(message: Message, state: FSMContext):

    await message.answer(
        (
            "Выберите товар для заказа. \n"
            "Для этого просто пришлите ссылку на сам товар из сайта POIZON."
        ),
        reply_markup=kbl.url_question_kb,
        parse_mode=ParseMode.HTML,
    )
    current_state = await state.get_state()

    if str(current_state) in str(FSMClient.edit_url):
        await state.set_state(FSMClient.edit_url_done)
    else:
        await state.set_state(FSMClient.waiting_for_product)


async def shoes_size(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if str(current_state) in str(FSMClient.waiting_for_product):
        validation = await valid.url_validate(message.text)
        if not validation:
            await message.answer(
                "Ссылка на товар некорректна.\n"
                "Пожалуйста, проверьте вводимые данные и попробуйте еще раз."
            )
            return await make_order(message, state)
        else:
            async with state.proxy() as data:
                data["url"] = message.text
            await state.set_state(FSMClient.waiting_for_size)
    else:
        await state.set_state(FSMClient.edit_size_done)

    await message.answer(
            "Введите нужный размер.",
            reply_markup=kbl.size_kb,
    )


async def shoes_price(message: Message, state: FSMContext):

    current_state = await state.get_state()

    await message.answer(
            text=(
                "Введите стоимость товара.\n"
                "Вводите цену, которая указана на сайте и только цифры."
            ),
            reply_markup=kbl.cancel_kb,
        )

    if str(current_state) in str(FSMClient.edit_price):
        await state.set_state(FSMClient.edit_price_done)
    else:
        async with state.proxy() as data:
            data["size"] = message.text
        await state.set_state(FSMClient.waiting_for_price)


async def addition(message: Message, state: FSMContext):

    current_state = await state.get_state()
    if str(current_state) in str(FSMClient.waiting_for_price):
        validation = await valid.price_validation(message.text)
        if not validation:
            await message.answer(
                "Цена некорректна.\n"
                "Проверьте вводимое значение и попробуйте еще раз."
            )
            return await shoes_price(message, state)
        else:
            async with state.proxy() as data:
                data["price"] = message.text
            await state.set_state(FSMClient.waiting_for_addition)
    else:
        await state.set_state(FSMClient.edit_addition_done)

    await message.answer(
        (
            "Вы можете оставить дополнительную информацию о товаре. \n"
            "Введите дополнительную информацию, например, расцветку."
        ),
        reply_markup=kbl.cancel_kb,
    )


async def approve_order(query: CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)

    async with state.proxy() as data:
        await sqlite_db.sql_add_order(data)
    await query.message.answer(
        "Ваш заказ был успешно принят на рассмотрение!"
        "\nCовсем скоро мы пришлём Вам реквизиты и стоимость заказа с учетом доп. условий!\n"
        "Ожидайте подтверждения заявки...",
        reply_markup=kb.client_keyboard,
    )

    data = await state.get_data()
    await msa.send_mess_to_admins(query.message, state)
    await state.set_state(FSMClient.start)


async def payment_information(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()
    order_id = await sqlite_db.get_order_id()
    money_info = await sqlite_db.get_money_info()
    price = await state.get_data()
    price = price["price"]
    user = await sqlite_db.sql_check_user("user_id", callback.message.chat.id)
    points = user[3]
    keyboard = kbl.payment_kb
    result_payment = int(price) * int(money_info[1]) + int(money_info[2])

    if str(current_state) in str(FSMPayment.use_points):
        keyboard = kbl.payment_use_points_kb
        result_payment = result_payment - points
        points = 0

    msg = (
        f"Номер заказа: {order_id}\n"
        f"Сумма к оплате: {result_payment} руб.\n"
        f"Количество BYN баллов: {points}"

    )

    async with state.proxy() as data:
        data["res_price"] = result_payment
        data["points"] = points
        data["order_id"] = order_id
        data["user_username"] = user[9]

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard,
    )
    await state.set_state(FSMPayment.payment)


async def use_points(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    async with state.proxy() as data:
        data["points_spend"] = data["points"]

    await sqlite_db.use_points(callback.message.chat.id)

    await state.set_state(FSMPayment.use_points)
    await payment_information(callback, state)


async def order_view(message: Message, state: FSMContext):

    current_state = await state.get_state()

    async with state.proxy() as data:
        if str(current_state) not in str(FSMClient.edit_all_done):
            if message.photo:
                data["photo_id"] = message.photo[-1].file_id
                data["additional_params"] = message.caption or ""
            else:
                data["additional_params"] = message.text
        data["stat"] = "Не обработан"
        data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['user_id'] = message.from_user.id


    if message.photo:
    # Отправить фото
        await message.bot.send_photo(
            message.chat.id,
            photo=data["photo_id"],  # Используем только первый id фото из списка
            caption=(
                "Ваш заказ: \n"
                f"{'Ссылка на товар:':<25} {data['url']}\n"
                f"{'Размер:':<25} {data['size']}\n"
                f"{'Цена:':<25} {data['price']}\n"
                f"{'Доп. информация:':<23} {data['additional_params']}"
            ),
            reply_markup=kbl.cancel_or_approve,
            parse_mode=ParseMode.HTML,
        )
    else:

        await message.answer(
            "Ваш заказ: \n"
            f"{'Ссылка на товар:':<25} {data['url']}\n"
            f"{'Размер:':<25} {data['size']}\n"
            f"{'Цена:':<25} {data['price']}\n"
            f"{'Доп. информация:':<23} {data['additional_params']}",
            reply_markup=kbl.cancel_or_approve
        )

    await state.set_state(FSMClient.waiting_for_approve)


async def edit_done(message: Message, state: FSMContext):

    current_state = await state.get_state()

    async with state.proxy() as data:

        if str(current_state) in str(FSMClient.edit_url_done):
            validation = await valid.url_validate(message.text)
            if validation:
                data['url'] = message.text
            else:
                await message.answer(
                    "Ссылка на товар некорректна.\n"
                    "Пожалуйста, проверьте вводимые данные и попробуйте еще раз."
                )
                await state.set_state(FSMClient.edit_url)
                return await make_order(message, state)
        elif str(current_state) in str(FSMClient.edit_price_done):
            validation = await valid.price_validation(message.text)
            if validation:
                data['price'] = message.text
            else:
                await message.answer(
                    "Цена некерректна.\n"
                    "Проверьте вводимое значение и попробуйте еще раз."
                )
                await state.set_state(FSMClient.edit_price)
                return await shoes_price(message, state)
        elif str(current_state) in str(FSMClient.edit_size_done):
            data['size'] = message.text
        else:
            if message.photo:
                data["photo_id"] = message.photo[-1].file_id
                data["additional_params"] = message.caption or ""
            else:
                data["additional_params"] = message.text

    await state.set_state(FSMClient.edit_all_done)
    await order_view(message, state)


async def edit_data(callback: Union[CallbackQuery, Message], state: FSMContext):

    if "url" in callback.data:
        await state.set_state(FSMClient.edit_url)
        await make_order(callback.message, state)

    elif "size" in callback.data:
        await state.set_state(FSMClient.edit_size)
        await shoes_size(callback.message, state)

    elif "cost" in callback.data:
        await state.set_state(FSMClient.edit_price)
        await shoes_price(callback.message, state)

    elif "info" in callback.data:
        await state.set_state(FSMClient.edit_addition)
        await addition(callback.message, state)


async def profile_view(message: Message, state: FSMContext):
    user = await sqlite_db.sql_check_user("user_id", message.chat.id)
    await message.answer(
        f"Пользователь: {user[9]}\n"
        f"Количество BYH баллов: {user[4]}\n"
        f"Количество заказов: {user[3]}\n"
        f"Номер аккаунта: {user[0]}\n"
        f"Привязан: VK/TG",
        reply_markup=kbl.profile_kb,
    )
    await state.set_state(FSMClient.profile_view)


async def go_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return None
    if current_state in str(FSMClient.waiting_for_name):
        await profile_view(callback.message, state)


async def change_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMClient.waiting_for_name)
    await callback.message.edit_text(
        text="Введите новое имя",
        reply_markup=kbl.name_change,
    )


async def change_name_db(message: Message, state: FSMContext):
    new_name = message.text
    if await sqlite_db.sql_check_user("username", new_name):
        await message.answer(
            "Такой никнейм уже занят.",
        )
        await profile_view(message, state)
    else:
        await sqlite_db.sql_update_username(message.from_user.id, new_name)
        await profile_view(message, state)


async def process_order_page(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    page_number = int(callback_query.data.split("#")[1]) if "#" in callback_query.data else 1
    await callback_query.message.edit_text(
        text=await sqlite_db.sql_check_order(callback_query.message, user_id, page_number),
        reply_markup=kbl.get_keyboard(user_id, page_number)
    )


async def view_sync_key(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="На данный момент раздел находистя в разработке...",
    )
    await profile_view(callback.message, state)


async def actual_money_course(message: Message, state: FSMContext):
    await message.answer(
        text="Введите стоимость товара в юанях",
        reply_markup=kbl.actual_course_kb,
    )
    await state.set_state(FSMClient.actual_course)


async def prise_calculation(message: Message, state: FSMContext):
    money_data = await sqlite_db.get_money_info()
    yuan_price = int(message.text)
    rub_price = yuan_price * int(money_data[0])
    total_price = rub_price + int(money_data[1])
    await message.answer(
        f"Курс: {money_data[0]}\n"
        f"Комиссия: {money_data[1]}\n"
        f"Стоимость без учета доставки: {total_price}\n"
        "Доставка оплачивается по прибытию."
    )


async def promo_activation(message: Message, state: FSMContext):
    await message.answer(
        "Введите промокод",
        reply_markup=kbl.cancel_kb,
    )
    await state.set_state(FSMClient.promo_activation)


async def promo_check(message: Message, state: FSMContext):
    promo_from_user = message.text
    promo, is_working = await sqlite_db.check_promo(promo_from_user)

    if not is_working:
        await message.answer(
            text="Такого промокода нет или превышен лимит использования",
            reply_markup=kbl.cancel_kb,
        )
    else:
        is_used = await sqlite_db.is_promo_used(promo_from_user, message.from_user.id)
        if not is_used:
            await message.answer(
                text="Промокод активирован!",
                reply_markup=kbl.cancel_kb,
            )
            await sqlite_db.update_promo(promo_from_user, promo[0], message.from_user.id)
        else:
            await message.answer(
                text="Такой промокод уже использован!",
                reply_markup=kbl.cancel_kb,
            )


async def poizon_install(message: Message, state: FSMContext):
    await message.answer(
        text=(
            "Здесь Вы сможете скачать приложение POIZON!\n"
            "Правда удобно?"
        ),
        reply_markup=kbl.poizon_install_kb
    )
    await state.set_state(FSMClient.pozion_install)


# async def pozion_file_load(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.message.edit_text(
#             text="Скачать POIZON",
#         )
# 
#         with open("poizon_apk/apk.txt", "rb") as file:
#             document = InputFile(file)
#             await callback.message.answer_document(
#                 document=document,
#                 reply_markup=kbl.cancel_kb,
#             )
#     except Exception as e:
#         print(f"Failed to send document: {e}")


async def sync_accounts(message: Message, state: FSMContext):
    await message.answer(
        text="Этот раздел находится в разработке...",
        reply_markup=kbl.cancel_kb,
    )
    await state.set_state(FSMClient.sync_accounts)


async def answer_to_question(message: Message, state: FSMContext):
    question_answer = await sqlite_db.answer_question()
    await message.answer(
        text=question_answer,
        reply_markup=kbl.cancel_kb,
    )
    await state.set_state(FSMClient.answer_to_question)


async def support(message: Message, state: FSMContext):
    await message.answer(
        text=(
            "Напишите нам если у вас возникли какие-то проблемы!\n"
            "Мы всегда рады Вам помочь!"
        ),
        reply_markup=kbl.support_kb,
    )
    await state.set_state(FSMClient.support)


async def cancel_order_to_eblan(callback: CallbackQuery, state: FSMContext):

    order_id = await oif.find_order_id(callback.message.text)

    data = await state.get_data()
    order_id = data['order_data'][0]

    await sqlite_db.delete_order(order_id)

    await callback.message.edit_text(
        text="Вы отменили заказ!",
        reply_markup=kbl.cancel_kb,
    )
    await state.set_state(FSMClient.cancel_order_to_eblan)
    await msa.send_mess_to_admins(callback.message, state, order_id)


async def eblan_pay_order(callback: CallbackQuery, state: FSMContext):

    order_id = await oif.find_order_id(callback.message.text)

    await callback.message.edit_text(
        text="Ожидайте подтверждения...",
        reply_markup=kbl.cancel_kb,
    )
    await state.set_state(FSMClient.eblan_pay_order)
    await msa.send_mess_to_admins(callback.message, state, order_id)


def register_handlers_client(DP: Dispatcher):
    DP.register_message_handler(
        command_start,
        commands=['start', 'help'],
        state="*",
    )
    DP.register_callback_query_handler(
        cancel_order,
        lambda query: "cancel" in query.data,
        state="*",
    )
    DP.register_message_handler(profile_view, lambda message: "Профиль" in message.text, state=["*", FSMClient.waiting_for_name])
    DP.register_callback_query_handler(change_name, lambda query: "ch_name" in query.data, state=FSMClient.profile_view)
    DP.register_callback_query_handler(view_sync_key, lambda query: "sync" in query.data, state=FSMClient.profile_view)
    DP.register_message_handler(change_name_db, state=FSMClient.waiting_for_name)
    DP.register_callback_query_handler(process_order_page, lambda query: "view_order" in query.data or (query.data.startswith("order_pg#")), state=FSMClient.profile_view)
    DP.register_callback_query_handler(go_back, lambda message: "back" in message.data, state=FSMClient.waiting_for_name)
    DP.register_message_handler(actual_money_course, lambda message: "Актуальный курс" in message.text, state="*")
    DP.register_message_handler(prise_calculation, state=FSMClient.actual_course)
    DP.register_message_handler(promo_activation, lambda message: "промокода" in message.text, state="*")
    DP.register_message_handler(promo_check, state=FSMClient.promo_activation)
    DP.register_message_handler(poizon_install, lambda message: "POIZON" in message.text, state="*")
    # DP.register_callback_query_handler(pozion_file_load, lambda query: "install" in query.data, state=FSMClient.pozion_install)
    DP.register_message_handler(sync_accounts, lambda message: "Синхронизация" in message.text, state="*")
    DP.register_message_handler(answer_to_question, lambda message: "Ответы на вопросы" in message.text, state="*")
    DP.register_message_handler(support, lambda message: "Служба" in message.text, state="*")

    DP.register_message_handler(
        edit_done,
        content_types=["text", "photo"],
        state=[
            FSMClient.url_validate,
            FSMClient.edit_url_done,
            FSMClient.edit_price_done,
            FSMClient.edit_size_done,
            FSMClient.edit_addition_done,
        ],
    )
    DP.register_message_handler(make_order, lambda message: "Сделать заказ" in message.text, state="*")
    DP.register_message_handler(shoes_price, state=[FSMClient.waiting_for_size, FSMClient.edit_price])
    DP.register_message_handler(
        order_view,
        content_types=["text", "photo"],
        state=[
            FSMClient.waiting_for_addition,
            FSMClient.edit_all_done,
        ],
    )
    # DP.register_message_handler(is_data_valid, state="*")
    DP.register_message_handler(shoes_size, state=[FSMClient.waiting_for_product, FSMClient.edit_size, FSMClient.data_validate])
    DP.register_message_handler(addition, state=[FSMClient.waiting_for_price, FSMClient.edit_addition])


    DP.register_callback_query_handler(edit_data, lambda query: query.data.startswith("edit"), state=FSMClient.waiting_for_approve)
    DP.register_callback_query_handler(approve_order, lambda query: "payment_confirm" in query.data, state=FSMPayment.payment)
    DP.register_callback_query_handler(payment_information, lambda query: "approve" in query.data, state=FSMClient.waiting_for_approve)
    DP.register_callback_query_handler(use_points, lambda query: "points_confirm" in query.data, state=FSMPayment.payment)
    DP.register_callback_query_handler(cancel_order_to_eblan, lambda query: "eblan" in query.data, state="*")
    DP.register_callback_query_handler(eblan_pay_order, lambda query: "pay_for_order" in query.data, state="*")
