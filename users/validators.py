import re

from django.forms import forms


def validate_phone(phone_number):
    # Валидация белорусского номера телефона
    if not re.match(r'^(\+375|80)(29|25|44|33)(\d{3})(\d{2})(\d{2})$', phone_number):
        raise forms.ValidationError('Введите корректный белорусский номер мобильного телефона в формате +375XXXXXXXXX.')


def validate_password(password_string):
    if not re.match(r'^(?=.*[A-Z])(?=.*[0-9]).{8,}$', password_string):
        if len(password_string) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
        if str(password_string).isdigit():
            raise forms.ValidationError('Пароль не может состоять только из цифр')
        if str(password_string).isalpha():
            raise forms.ValidationError('В пароле должна быть хотя бы одна цифра')
        if str(password_string).isupper():
            raise forms.ValidationError('В пароле должен быть хотя бы один символ нижнего регистра')
        if str(password_string).islower():
            raise forms.ValidationError('В пароле должен быть хотя бы один символ верхнего регистра')




def validate_email(email):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise forms.ValidationError('Некорректный адрес электронной почты')
