import re


async def find_order_id(text):
    match = re.search(r'byhedzy-(\d+)', text)

    if match:
        order_number = match.group(1)
        return order_number
    return None


async def find_user_id(text):
    match_order = re.search(r'номером (\d+)', text)
    match_user = re.search(r'tg_id: (\d+)', text)

    if match_order and match_user:
        order_number = match_order.group(1)
        user_id = match_user.group(1)
        return order_number, user_id
    else:
        return None, None
