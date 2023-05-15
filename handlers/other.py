import os
import asyncio
from datetime import datetime, time
import pytz
import aiohttp

from dotenv import load_dotenv

from database import sqlite_db as db

load_dotenv()
APP_ID = os.getenv("COURSE_KEY")


# Функция для получения текущего времени по Московскому времени
def get_current_moscow_time():
    moscow_timezone = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_timezone).time()
    current_time_formatted = current_time.strftime('%H:%M')
    return current_time_formatted


# Функция для обновления курса валют

async def update_exchange_rate():
    # Проверка времени
    target_time = time(11, 35).strftime('%H:%M') # Целевое время обновления курса
    current_time = get_current_moscow_time()

    print('aa')

    if current_time != target_time:
        return

    # Ваш код для обновления курса валют
    CURRENCY_CNY = 'CNY'
    CURRENCY_RUB = 'RUB'

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://openexchangerates.org/api/latest.json?app_id={APP_ID}&symbols={CURRENCY_CNY}') as response_uan:
            async with session.get(f'https://openexchangerates.org/api/latest.json?app_id={APP_ID}&symbols={CURRENCY_RUB}') as response_rub:

                if response_uan.status == 200 and response_rub.status == 200:
                    data_uan = await response_uan.json()
                    data_rub = await response_rub.json()

                    print(data_uan['rates'])

                    rate_uan = data_uan['rates'][CURRENCY_CNY]
                    rate_rub = data_rub['rates'][CURRENCY_RUB]

                    rate = round(rate_rub / rate_uan, 2)

                    await db.update_course(rate)


# Запуск функции обновления курса валют в бесконечном цикле
async def run_update_loop():
    print("Обновление курса валют запущено")
    while True:
        await update_exchange_rate()
        await asyncio.sleep(3)  # Проверка каждую минуту
