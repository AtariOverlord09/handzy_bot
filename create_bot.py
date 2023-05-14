import os

from dotenv import load_dotenv
from aiogram import Bot, dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


load_dotenv()

storage = MemoryStorage()

TOKEN = os.getenv('TOKEN')

BOT = Bot(token=TOKEN)
DP = dispatcher.Dispatcher(BOT, storage=storage)

