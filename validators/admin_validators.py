"""Валидаторы для админа."""
import re


async def is_digit_validation(price):
    """Валидация цены продукта."""
    if price.isdigit():
        return True
    return False


async def validate_course_commission(text: str) -> bool:
    pattern = r'^Курс:\s+([\d.]+);\s+Комиссия:\s+([\d.]+);$'
    match = re.match(pattern, text)
    if match is None:
        return False, False
    course, commission = match.groups()
    try:
        course = float(course)
        commission = float(commission)
    except ValueError:
        return False, False
    return course, commission


async def validate_faq(text):

    pattern = r'\?(.*?)\s!(.*?);'
    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        results = []
        for match in matches:
            question = match[0].strip()
            answer = match[1].strip()
            results.append((question, answer))
        return results
    else:
        return None
