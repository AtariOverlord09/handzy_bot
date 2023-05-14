'''Валидаторы сообщений от пользователя.'''


async def url_validate(link):
    """Валидация ссылки на продукт."""
    if "https://" not in link and "http://" not in link:
        return False
    return True


async def price_validation(price):
    """Валидация цены продукта."""
    if price.isdigit() and int(price) > 0:
        return True
    return False
