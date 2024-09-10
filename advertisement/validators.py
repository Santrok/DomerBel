from django.forms import forms
from django.core.cache import cache


def validate_words(text):
    bw = cache.get('bad_words')
    if bw is None:
        from .models import BadWords
        bw = BadWords.objects.all()
        cache.set('bad_words', bw)
    text = text.lower()
    for i in bw:
        if i.word in text:
            raise forms.ValidationError(f'Найдено запрещенное слово')