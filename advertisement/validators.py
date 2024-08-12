from django.forms import forms
from django.core.cache import cache


def validate_words(text):
    print('bad_words')
    bw = cache.get('bad_words')
    if bw is None:
        from .models import BadWords
        bw = BadWords.objects.all()
        cache.set('bad_words', bw)
    # from .models import BadWords
    # bw = BadWords.objects.all()
    # print(bw)
    text = text.lower()
    for i in bw:
        if i.word in text:
            raise forms.ValidationError(f'Найдено запрещенное слово')