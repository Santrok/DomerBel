from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_ckeditor_5.widgets import CKEditor5Widget

from advertisement.forms import ImagePreviewWidget
from main_page_domer.models import Publication

from .models import User, Message
from .validators import validate_password, validate_email, validate_phone


class EditContactDataForm(forms.ModelForm):
    first_name = forms.CharField(required=True, error_messages={'required': 'Не указано контактное лицо'},
                                 widget=forms.TextInput(attrs={'class': 'input_field'}),
                                 label='Контактное лицо')
    phone_number = forms.CharField(required=True, error_messages={'required': 'Не указан номер телефона'},
                                   widget=forms.TextInput(attrs={'class': 'input_field'}),
                                   validators=[validate_phone],
                                   label='Телефон')
    email = forms.EmailField(required=True, error_messages={'required': 'Не указан email'},
                             widget=forms.TextInput(attrs={'class': 'input_field'}),
                             validators=[validate_email],
                             label='E-MAIL')

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'email', 'phone_number']


class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(error_messages={'required': 'Введите старый пароль'},
                               label='Введите старый пароль',
                               widget=forms.PasswordInput(
                                   attrs={'class': 'input_field', 'placeholder': 'Введите старый пароль'}),
                               validators=[validate_password])
    new_password = forms.CharField(error_messages={'required': 'Введите новый пароль'}, widget=forms.PasswordInput(
        attrs={'class': 'input_field', 'placeholder': 'Введите новый пароль'}),
                                   validators=[validate_password], label='Введите новый пароль')
    repeat_new_pass = forms.CharField(error_messages={'required': 'Повторите новый пароль'}, widget=forms.PasswordInput(
        attrs={'class': 'input_field', 'placeholder': 'Повторите новый пароль'}),
                                      validators=[validate_password], label='Повторите новый пароль')

    class Meta:
        model = get_user_model()
        fields = ['password']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        repeat_new_pass = cleaned_data.get('repeat_new_pass')
        if new_password is not None and repeat_new_pass is not None and new_password != repeat_new_pass:
            self.add_error('repeat_new_pass', 'Пароли не совпадают')


class MessageForm(forms.ModelForm):
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'message_input'}))

    class Meta:
        model = Message
        fields = ['message']


class MyCustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'announcement', 'description', 'preview_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['announcement'].widget = CKEditor5Widget(config_name='extends2')
        self.fields['preview_image'].widget = ImagePreviewWidget()
        self.fields['preview_image'].widget.attrs.update({"id": "id_preview_image"})
        self.fields['announcement'].required = False
        self.fields['description'].required = False


class MessageForm(forms.ModelForm):
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'message_input'}))

    class Meta:
        model = Message
        fields = ['message']

