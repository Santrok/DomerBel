from django import forms
from django.core.validators import FileExtensionValidator

from advertisement.models import ReasonOfComplaint


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'zip'])])


class ComplaintForm(forms.Form):
    user = forms.EmailField(required=True,
                            error_messages={'required': 'Не указан email'},
                            label='Ваш e-mail:',
                            widget=forms.EmailInput(attrs={'class': 'input_field'}))
    reason = forms.ModelChoiceField(queryset=ReasonOfComplaint.objects.all(),
                                    required=True,
                                    empty_label="Выберите причину",
                                    label="Причина жалобы:",
                                    widget=forms.Select(attrs={'class': 'input_field'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'input_field'}),
                           required=True,
                           error_messages={'required': 'Отсутствует текст обоснования'},
                           label='Обоснование жалобы:')

    def clean_reason(self):
        reason = self.cleaned_data['reason']
        if reason == '0':
            self.add_error('reason', 'Не выбрана причина жалобы')
        return reason
