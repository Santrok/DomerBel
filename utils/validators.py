import re

from django.core.cache import cache
from django.core.exceptions import ValidationError

from main.models import BadWords


def validate_phone(phone_number):
    """
    Валидация белорусского номера телефона
    """

    if not re.match(r'^(?:\+7|8)?[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}$|^(?:\+375|80)[ -]?\(?\d{2}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}$', phone_number):
        raise ValidationError('Введите корректный номер мобильного телефона РБ и РФ.')


def validate_words(text):
    """
    Валидация текста на содержание запрещенных слов
    """
    bw = cache.get('bad_words')
    if bw is None:
        bw = BadWords.objects.all()
        cache.set('bad_words', bw)
    text = text.lower()
    for i in bw:
        if i.word in text:
            raise ValidationError(f'Найдено запрещенное слово')
