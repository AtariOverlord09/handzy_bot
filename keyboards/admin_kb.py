from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создадим класс меню админа, экземпляром которого будет клавиатура


class AdminMenuKeyboard:
    def __init__(self):
        self.keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        self.keyboard.add(
            KeyboardButton('Просмотр пользователей и заказов')
        )
        self.keyboard.add(
            KeyboardButton('Изменение реквизитов'),
            KeyboardButton('Изменить комиссию и/или курс валюты'),
        )
        self.keyboard.add(
            KeyboardButton('Создание промокодов'),
            KeyboardButton('Изменение информации')
        )
        self.keyboard.add(
            KeyboardButton('Изменение контактов'),
            KeyboardButton('Изменение APK файла'),
        )

    def get_keyboard(self):
        return self.keyboard
