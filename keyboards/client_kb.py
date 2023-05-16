from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Создаем кнопки для клавиатуры
order_button = KeyboardButton('🛒Сделать заказ🛒')
profile_button = KeyboardButton('🥷Профиль🥷')
currency_button = KeyboardButton('💱Актуальный курс и комиссия💱')
promo_button = KeyboardButton('🎁Активация промокода🎁')
download_button = KeyboardButton('📥Скачать POIZON📥')
sync_button = KeyboardButton('🔄Синхронизация аккаунта🔄')
faq_button = KeyboardButton('❓Ответы на вопросы❓')
support_button = KeyboardButton('🆘Служба поддержки🆘')

# Создаем клавиатуру
client_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

# Добавляем кнопки в клавиатуру
client_keyboard.add(order_button, profile_button)
client_keyboard.add(currency_button, promo_button)
client_keyboard.add(download_button, sync_button)
client_keyboard.add(faq_button, support_button)

# Создаем клавиатуру, которая будет использоваться для удаления текущей клавиатуры
remove_keyboard = ReplyKeyboardRemove()
