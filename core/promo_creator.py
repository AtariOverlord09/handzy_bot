import random
import string


async def generate_promo_code(length):
    characters = string.ascii_letters + string.digits
    promo_code = ''.join(random.choice(characters) for _ in range(length))
    return promo_code.upper()
