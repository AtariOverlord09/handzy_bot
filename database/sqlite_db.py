import sqlite3 as sq


def sql_start():
    base = sq.connect('byhedzy.db')
    if base:
        print('База данных подключена.')
    base.execute(
        'CREATE TABLE IF NOT EXISTS'
        ' orders('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' product_code TEXT,'
        ' url TEXT,'
        ' size TEXT,'
        ' price INTEGER CHECK(price > 0),'
        ' additional_info TEXT,'
        ' payment_amount INTEGER CHECK(payment_amount > 0),'
        ' shipping_amount INTEGER CHECK(shipping_amount > 0),'
        ' date TEXT,'
        ' points_spent INTEGER CHECK(points_spent >= 0),'
        ' status TEXT,'
        ' user_id INTEGER REFERENCES users(id),'
        ' account_number TEXT)'
    )
    base.execute(
        'CREATE TABLE IF NOT EXISTS'
        ' users('
        ' id INTEGER PRIMARY KEY AUTOINCREMENT,'
        ' user_id TEXT,'
        ' orders_count INTEGER CHECK(orders_count >= 0),'
        ' points INTEGER CHECK(points >= 0),'
        ' promo_codes TEXT,'
        ' vk_link TEXT,'
        ' tg_link TEXT,'
        ' registration_date TEXT,'
        ' last_order_date TEXT)'
    )
    base.execute('''
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            promo_code TEXT UNIQUE,
            amount INTEGER CHECK(amount > 0),
            activations INTEGER CHECK(activations >= 0),
            activated BOOLEAN DEFAULT FALSE
        );
    ''')
    base.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT
        );
    ''')
    base.execute('''
        CREATE TABLE IF NOT EXISTS money_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actual_course INTEGER CHECK(actual_course >= 0)
        );
    ''')
    base.execute('''
        CREATE TABLE IF NOT EXISTS question_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        );
    ''')
    base.execute('''
        CREATE TABLE  IF NOT EXISTS user_promo_codes (
            user_id INTEGER REFERENCES users(user_id),
            promo_code_id INTEGER REFERENCES promo_codes(id),
            PRIMARY KEY (user_id, promo_code_id)
        );
    ''')
    # base.execute('''INSERT INTO admins (username, admin_id, tg_link) VALUES ("hedzy", 1908259603, "https://t.me/hedzy666")''')

    # update_admin_record(admin_id=5155740269, username="Admin1", tg_link="https://t.me/GelliToMellopy")
    # delete_all_records()

    base.commit()
    base.close()


async def sql_add_order(data, edit=False):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    if edit:
        print(data)
        # Если заказ уже существует, обновляем значения атрибутов
        if 'photo_id' in data:
            cur.execute(
                'UPDATE orders SET product_code = ?, url = ?, size = ?, price = ?, additional_info = ?, payment_amount = ?, shipping_amount = ?, date = ?, points_spent = ?, status = ?, user_id = ?, account_number = ?, photo_id = ? '
                'WHERE id = ?',
                data[1:] + (data[0], )
            )
        else:
            cur.execute(
                'UPDATE orders SET product_code = ?, url = ?, size = ?, price = ?, additional_info = ?, payment_amount = ?, shipping_amount = ?, date = ?, points_spent = ?, status = ?, user_id = ?, account_number = ?, photo_id = ? '
                'WHERE id = ?',
                data[1:] + (data[0], )
            )
    else:
        # Если заказ не существует, создаем новую запись
        if 'photo_id' in data:
            cur.execute(
                'INSERT INTO orders (url, size, price, photo_id, additional_info, payment_amount, date, points_spent, status, user_id) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (data['url'], data['size'], data['price'], data['photo_id'], data['additional_params'], data["res_price"], data['date'], data.get('points_spent', 0), data["stat"], data['user_id'])
            )
        else:
            cur.execute(

                'INSERT INTO orders (url, size, price, additional_info, payment_amount, date, points_spent, status, user_id) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (data['url'], data['size'], data['price'], data['additional_params'], data["res_price"], data['date'], data.get('points_spent', 0), data["stat"], data['user_id'])
            )

    base.commit()
    base.close()


async def sql_add_user(data):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute(
        'INSERT INTO users (user_id, username, orders_count, points, promo_codes, vk_link, tg_link, registration_date, last_order_date) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        tuple(data.values())
    )
    base.commit()
    base.close()


async def sql_check_user(field_name, search_field):
    conn = sq.connect('byhedzy.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {field_name}=?", (search_field,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


async def sql_update_username(user_id, new_username):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute(
        'UPDATE users SET username = ? WHERE user_id = ?',
        (new_username, user_id),
    )
    base.commit()
    base.close()


async def read_order_data(message):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()   
    await message.answer('Спасибо за заказ. Ваш заказ принят.')
    for data in cur.execute("SELECT * FROM orders").fetchall():
        await message.answer(
            f'Ссылка: {data[1]}\n'
            f'Размер: {data[2]}\n'
            f'Цена: {data[3]}\n'
            f'Дата: {data[4]}\n'
            f'Доп. параметры: {data[5]}'
        )
    base.close()


async def sql_check_order(message, user_id, page_number):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    records_per_page = 3
    offset = records_per_page * (page_number - 1)
    user_orders = cur.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?,?",
        (user_id, offset, records_per_page),
    ).fetchall()
    print(user_orders)
    if not user_orders:
        if page_number == 1:
            await message.edit_text('У Вас ещё нет заказов!')
        else:
            await message.edit_text('У Вас более нет заказов')
    else:
        answe_r = ""
        for data in user_orders:
            answe_r += (
                f'\n\nСсылка: {data[2]}\n'
                f'Размер: {data[3]}\n'
                f'Цена: {data[4]}\n'
                f'Дата: {data[8]}\n'
                f'Доп. параметры: {data[5]}'
            )
            if data[13] is not None:
                answe_r += '\nФото: Прикреплено'
    base.close()
    return answe_r


async def get_orders_count(user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    order_count = (cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,)).fetchone()[0] + 2) // 3
    base.close()
    return order_count


async def get_money_info():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    money_info = cur.execute("SELECT * FROM money_info ORDER BY id DESC LIMIT 1").fetchone()
    base.close()
    return money_info


async def check_promo(promo_code):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    promo = cur.execute("SELECT * FROM promo_codes WHERE activated<activations AND LOWER(promo_code)=LOWER(?)", (promo_code,)).fetchone()
    base.close()
    if promo:
        return promo, True
    return promo, False


async def get_promo(promo):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    promo = cur.execute("SELECT amount FROM promo_codes WHERE promo_code=?", (promo,)).fetchone()
    base.close()
    return promo


async def update_promo(promo_code, promo_id, user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute("INSERT INTO user_promo_codes (user_id, promo_code_id) VALUES (?, ?)", (user_id, promo_id))
    cur.execute("UPDATE promo_codes SET activated=activated+1 WHERE promo_code=?", (promo_code,))
    amount = cur.execute('''SELECT amount FROM promo_codes WHERE promo_code=?''', (promo_code,)).fetchone()
    cur.execute('''UPDATE users SET points=points+? WHERE user_id=?''', (amount[0], user_id))
    base.commit()
    base.close()


async def is_promo_used(promo_code, user_id):
    conn = sq.connect('byhedzy.db')
    cur = conn.cursor()

    # Fetch the promo code ID
    cur.execute("SELECT id FROM promo_codes WHERE promo_code=?", (promo_code,))
    promo_id = cur.fetchone()

    if promo_id:
        # Check if the user has used the promo code
        cur.execute("SELECT * FROM user_promo_codes WHERE promo_code_id=? AND user_id=?", (promo_id[0], user_id))
        user_promo = cur.fetchone()

        conn.close()

        if user_promo:
            return True

    conn.close()
    return False


async def answer_question():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    question_answer = cur.execute("SELECT * FROM question_answers ORDER BY id DESC").fetchall()
    base.close()
    result_qa = ""
    for qa in question_answer:
        result_qa += f"\nВопрос: {qa[1]}\nОтвет: {qa[2]}\n\n"
    return result_qa


async def get_admin(user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    admin = cur.execute("SELECT * FROM admins WHERE admin_id=?", (user_id,)).fetchone()
    base.close()
    return admin


async def insert_money_info(course, comission):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    money_info = cur.execute('''SELECT * FROM money_info''').fetchone()
    if money_info is None:
        cur.execute("INSERT INTO money_info (actual_course, commission) VALUES (?, ?)", (course, comission))
    else:
        cur.execute("UPDATE money_info SET actual_course=?, commission=? WHERE id=1", (course, comission))
    base.commit()
    base.close()


async def update_comission(comission):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute("UPDATE money_info SET commission=? WHERE id=1", (comission,))
    base.commit()
    base.close()


async def update_course(course):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute("UPDATE money_info SET actual_course=? WHERE id=1", (course,))
    base.commit()
    base.close()


async def change_requisites(req):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute("UPDATE money_info SET requisites=? WHERE id=1", (req,))
    base.commit()
    base.close()


async def insert_promo(data):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute("INSERT INTO promo_codes (promo_code, amount, activations) VALUES (?, ?, ?)", (data["promo"], data["value"], data["activation"]))
    base.commit()
    base.close()


async def get_promo_list(message, page_number):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    records_per_page = 3
    offset = records_per_page * (page_number - 1)
    user_orders = cur.execute(
        "SELECT * FROM promo_codes ORDER BY id DESC LIMIT ?,?",
        (offset, records_per_page),
    ).fetchall()
    base.close()
    if not user_orders:
        if page_number == 1:
            await message.edit_text('У Вас ещё нет промокодов!')
        else:
            await message.edit_text('У Вас более нет заказов')
    else:
        answe_r = ""
        for data in user_orders:
            answe_r += (
                f'\n\nid: {data[0]}\n'
                f'Промокод: {data[1]}\n'
                f'Сумма: {data[2]}\n'
                f'Количество активаций: {data[3]}\n'
                f'Активированно: {data[4]}'
            )
    return answe_r


def get_promo_count():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    promo_count = (cur.execute("SELECT COUNT(*) FROM promo_codes").fetchone()[0] + 2) // 3
    base.close()
    return promo_count


async def sql_insert_faq(faq_comb):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    for faq in faq_comb:
        cur.execute("INSERT INTO question_answers (question, answer) VALUES (?, ?)", (faq[0], faq[1]))
    base.commit()
    base.close()


def update_admin_record(admin_id: int, tg_link: str, username: str=None):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    cur.execute("SELECT * FROM admins WHERE admin_id=?", (admin_id,))
    existing_record = cur.fetchone()

    if existing_record:
        # Обновляем существующую запись
        cur.execute("UPDATE admins SET username=?, tg_link=? WHERE admin_id=?",
                       (username, tg_link, admin_id))
    else:
        # Создаем новую запись
        cur.execute("INSERT INTO admins (username, admin_id, tg_link) VALUES (?, ?, ?)",
                    (username, admin_id, tg_link))

    # Сохраняем изменения и закрываем соединение с базой данных
    base.commit()
    base.close()


async def get_orders_for_admin(message, page_number):

    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    records_per_page = 3
    offset = records_per_page * (page_number - 1)
    user_orders = cur.execute(
        "SELECT * FROM orders ORDER BY id DESC LIMIT ?,?",
        (offset, records_per_page),
    ).fetchall()

    base.close()

    if not user_orders:
        if page_number == 1:
            await message.edit_text('У Вас ещё нет заказов!')
        else:
            await message.edit_text('У Вас более нет заказов!')
    else:
        answe_r = ""
        for data in user_orders:
            answe_r += (
                f'\n\nНомер заказа: {data[0]}\n'
                f'Артикул: {data[1]}\n'
                f'Размер: {data[3]}\n'
                f'Дата заказа: {data[8]}\n'
                f'Статус: {data[10]}'
            )
    answe_r += f'\n\nСтраница: {page_number}'
    answe_r += '\nДля выбора введите номер заказа'

    return answe_r


async def get_orders_admin_count():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    order_count = (cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0] + 2) // 3
    base.close()
    return order_count


def delete_all_records():
    # Подключение к базе данных
    base = sq.connect('byhedzy.db')
    cursor = base.cursor()

    # Получение списка таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Удаление всех записей из каждой таблицы
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DELETE FROM {table_name};")

    # Сохранение изменений и закрытие соединения с базой данных
    base.commit()
    base.close()


async def get_order_detail(order_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    order_detail = cur.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    base.close()
    return order_detail


async def get_amount_for_order(user_id):
    conn = sq.connect('byhedzy.db')
    cur = conn.cursor()
    print(user_id)

    # Get the last promo code used by the user
    cur.execute('''SELECT promo_code_id FROM user_promo_codes WHERE user_id=? ORDER BY ROWID DESC LIMIT 1''', (user_id,))
    promo_id = cur.fetchone()

    if promo_id:
        promo_id = promo_id[0]

        # Check if the promo code is used
        cur.execute('''SELECT is_used FROM user_promo_codes WHERE promo_code_id=?''', (promo_id,))
        is_used = cur.fetchone()
        print(is_used)

        if is_used and is_used[0] == 1:
            # Promo code is used, return zero
            conn.close()
            return 0

        # Get the amount for the last promo code used by the user
        cur.execute('''SELECT amount FROM promo_codes WHERE id=?''', (promo_id,))
        amount = cur.fetchone()

        cur.execute('''UPDATE user_promo_codes SET is_used=1 WHERE promo_code_id=?''', (promo_id,))

        conn.commit()
        conn.close()

        if amount:
            return amount[0]

    conn.close()
    return 0


async def last_order_date(user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    last_date = cur.execute('''SELECT date FROM orders WHERE user_id=? ORDER BY ROWID DESC LIMIT 1''', (user_id,)).fetchone()
    base.close()

    if last_date:
        last_date = last_date[0]
    else:
        last_date = None

    return last_date


async def get_user_list(message, page_number):

    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    records_per_page = 3
    offset = records_per_page * (page_number - 1)
    user_list = cur.execute(
        "SELECT * FROM users ORDER BY id DESC LIMIT ?,?",
        (offset, records_per_page),
    ).fetchall()

    print(user_list)

    base.close()

    if not user_list:
        if page_number == 1:
            await message.edit_text('У Вас ещё нет заказов!')
        else:
            await message.edit_text('У Вас более нет заказов!')
    else:
        answe_r = ""
        for data in user_list:

            answe_r += (
                f'\n\nПользователь: {data[9]}\n'
                f'Количество BYN баллов: {data[3]}\n'
                f'Количество заказов: {data[2]}\n'
                f'Дата послед. заказа: {data[8]}\n'
                f'Номер аккаунта: {data[0]}\n'
            )
    answe_r += f'\n\nСтраница: {page_number}'
    answe_r += '\nДля выбора введите ник или номер пользователя'

    return answe_r


async def get_users_count():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    user_count = (cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] + 2) // 3
    base.close()
    return user_count


async def get_user_detail_orders(user_id, page_number):

    base = sq.connect('byhedzy.db')
    cur = base.cursor()

    records_per_page = 3
    offset = records_per_page * (page_number - 1)
    user_orders = cur.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?,?",
        (user_id, offset, records_per_page),
    ).fetchall()

    base.close()

    if not user_orders:
        if page_number == 1:
            answe_r = "У вас еще нет заказов!"
        else:
            answe_r = "У Вас более заказов!"
    else:
        answe_r = ""
        for data in user_orders:
            print(data)
            answe_r += (
                f'\n\nНомер заказа: {data[0]}\n'
                f'Артикул: {data[1]}\n'
                f'Размер: {data[3]}\n'
                f'Дата заказа: {data[8]}\n'
                f'Статус: {data[10]}'
            )
        answe_r += f'\n\nСтраница: {page_number}'
        answe_r += '\nДля выбора введите номер заказа'

    return answe_r


async def get_user_detail_orders_count(user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    order_count = (cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,)).fetchone()[0] + 2) // 3
    base.close()
    return order_count


async def update_user(data):
    conn = sq.connect("byhedzy.db")
    cur = conn.cursor()

    try:

        cur.execute('''UPDATE users SET username=?, points=? WHERE user_id=?''', (data[9], data[3], data[1]))

        conn.commit()
        conn.close()
    except Exception as e:
        # Handle the exception accordingly
        print(f"An error occurred: {str(e)}")
        conn.rollback()
        conn.close()


async def delete_user(user_id):
    conn = sq.connect("byhedzy.db")
    cur = conn.cursor()

    try:
        cur.execute('''DELETE FROM users WHERE user_id=?''', (user_id,))
        cur.execute('''DELETE FROM orders WHERE user_id=?''', (user_id,))
        cur.execute('''DELETE FROM user_promo_codes WHERE user_id=?''', (user_id,))

        conn.commit()
        conn.close()
    except Exception as e:
        # Handle the exception accordingly
        print(f"An error occurred: {str(e)}")
        conn.rollback()
        conn.close()


async def get_order_id():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    order_id = cur.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1").fetchone()
    base.close()
    if order_id:
        return order_id[0] + 1
    return 1


async def use_points(user_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute('''UPDATE users SET points=0 WHERE user_id=?''', (user_id,))
    base.commit()
    base.close()


async def get_all_admins():
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    admins = cur.execute("SELECT admin_id FROM admins").fetchall()
    base.close()
    return admins


async def delete_order(order_id):
    base = sq.connect('byhedzy.db')
    cur = base.cursor()
    cur.execute('''DELETE FROM orders WHERE id=?''', (order_id,))
    base.commit()
    base.close()
