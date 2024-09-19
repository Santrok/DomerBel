from django import forms
from django_recaptcha.fields import ReCaptchaField

from main_page_domer.models import ReasonOfComplaint
from users.validators import validate_email


class FeedbackForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': 'Не указан email'}, label='Ваш e-mail:',
                             validators=[validate_email], widget=forms.EmailInput(attrs={'class': 'input_field'}))
    subject = forms.CharField(required=True, max_length=255, error_messages={'required': 'Не указана тема письма'},
                            label="Тема письма:", widget=forms.TextInput(attrs={'class': 'input_field'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'input_field'}), required=True,
                              error_messages={'required': 'Отсутствует текст письма'}, label='Текст письма:')
    captcha = ReCaptchaField(label='')


class ComplaintForm(forms.Form):
    user = forms.EmailField(required=True, error_messages={'required': 'Не указан email'}, label='Ваш e-mail:',
                             validators=[validate_email], widget=forms.EmailInput(attrs={'class': 'input_field'}))
    reason = forms.ModelChoiceField(queryset=ReasonOfComplaint.objects.all(), required=True,
                                    empty_label="Выберите причину", label="Причина жалобы:",
                                    widget=forms.Select(attrs={'class': 'input_field'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'input_field'}), required=True,
                              error_messages={'required': 'Отсутствует текст обоснования'}, label='Обоснование жалобы:')

    def clean_reason(self):
        reason = self.cleaned_data['reason']
        if reason == '0':
            self.add_error('reason', 'Не выбрана причина жалобы')
        return reason


class PaidForm(forms.Form):
    id_advertisement = forms.IntegerField(label='ID объявления')
    vip = forms.BooleanField(label='Сделать VIP-объявлением: 5руб', required=False)
    highlight_ad = forms.BooleanField(label='Выделить объявление: 3руб', required=False)
    special_accommodation = forms.BooleanField(label='Спецразмещение: 2руб', required=False)
    raise_in_search = forms.BooleanField(label='Поднять в поиске: 1руб', required=False)

