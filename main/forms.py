from django import forms
from django_recaptcha.fields import ReCaptchaField


class FeedbackForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': 'Не указан email'},
                             label='Ваш e-mail:',
                             widget=forms.EmailInput(attrs={'class': 'input_field'}))
    subject = forms.CharField(required=True,
                              max_length=255,
                              error_messages={'required': 'Не указана тема письма'},
                              label="Тема письма:",
                              widget=forms.TextInput(attrs={'class': 'input_field'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'input_field'}),
                              required=True,
                              error_messages={'required': 'Отсутствует текст письма'},
                              label='Текст письма:')
    captcha = ReCaptchaField(label='')
