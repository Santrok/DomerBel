from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from api.validators import validate_password
from utils.validators import validate_phone


class EditContactDataForm(forms.ModelForm):
    phone_number = forms.CharField(required=True,
                                   error_messages={'required': 'Не указан номер телефона'},
                                   widget=forms.TextInput(attrs={'class': 'input_field'}),
                                   validators=[validate_phone],
                                   label='Телефон')

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'email', 'phone_number']
        labels = {
            "first_name": "Контактное лицо",
            "email": "E-MAIL"
        }
        error_messages = {
            "first_name": {'required': "Не указано контактное лицо"},
            "email": {'required': "Не указан email"}
        }


class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(error_messages={'required': 'Введите старый пароль'},
                               required=True,
                               label='Введите старый пароль',
                               widget=forms.PasswordInput(attrs={'placeholder': 'Введите старый пароль'}),
                               validators=[validate_password])
    new_password = forms.CharField(error_messages={'required': 'Введите новый пароль'},
                                   required=True,
                                   widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'}),
                                   validators=[validate_password],
                                   label='Введите новый пароль')
    repeat_new_pass = forms.CharField(error_messages={'required': 'Повторите новый пароль'},
                                      required=True,
                                      widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'}),
                                      validators=[validate_password],
                                      label='Повторите новый пароль')

    class Meta:
        model = get_user_model()
        fields = ['password']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        repeat_new_pass = cleaned_data.get('repeat_new_pass')
        if new_password is not None and repeat_new_pass is not None and new_password != repeat_new_pass:
            self.add_error('repeat_new_pass', 'Пароли не совпадают')


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["email", ]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ["email", ]
