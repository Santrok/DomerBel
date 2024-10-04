from functools import partial
from itertools import groupby
from operator import attrgetter
from string import Template

from django import forms
from django.forms.models import ModelChoiceIterator, ModelChoiceField
from django.utils.safestring import mark_safe

from advertisement.models import Region, Category, Store

from users.validators import validate_phone
from django.core.validators import FileExtensionValidator


class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        if value:
            html = Template(
                f'{input_html}<div class="photo_img"><div class="delete_img"></div><img src="$link"/></div>')
            img_html = mark_safe(html.substitute(link=value.url))
            return img_html
        return input_html


class GroupedModelChoiceIterator(ModelChoiceIterator):
    """Расширение базового класса и переопределение итератора для создания
        сгруппированных значений optgroup селектора выбора"""

    def __init__(self, field, group_by):
        self.group_by = group_by
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.group_by):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(ModelChoiceField):
    """Расширение базового класса для создания
        селектора выбора с использованием расширенного итератора"""

    def __init__(self, *args, choices_group_by, **kwargs):
        if isinstance(choices_group_by, str):
            choices_group_by = attrgetter(choices_group_by)
        elif not callable(choices_group_by):
            raise TypeError(
                'choice_group_by должен быть либо строкой, либо вызываемым объектом, принимающим один аргумент')
        self.iterator = partial(GroupedModelChoiceIterator, group_by=choices_group_by)
        super().__init__(*args, **kwargs)


class StoreForm(forms.ModelForm):
    region = forms.ModelChoiceField(queryset=Region.objects.filter(type="Город"),
                                    label="Регион, город, область")

    category = GroupedModelChoiceField(queryset=Category.objects.filter(level=1).prefetch_related('parent'),
                                       choices_group_by='parent',
                                       label="Раздел",
                                       widget=forms.Select(attrs={'size': 10}), empty_label=None)
    phone_num = forms.CharField(max_length=255,
                                required=False,
                                label="Телефон",
                                validators=[validate_phone])
    logo_image = forms.ImageField(required=True,
                                  label="Логотип",
                                  widget=ImagePreviewWidget(attrs={"id": "id_logo_image"}))

    class Meta:
        model = Store
        fields = ['region', 'address', 'category', 'title', 'slug', 'description', 'url', 'contact_name', 'email',
                  'phone_num', 'video_link', 'logo_image']
        labels = {
            "slug": """Имя магазина, которое будет отображаться в URL-e страницы Вашего магазина 
                    (только латинские буквы и тире, должно начинаться с буквы и до 30 символов""",
        }
        widgets = {
            "email": forms.TextInput(attrs={'id': 'store_email'}),
            "video_link": forms.URLInput(attrs={'placeholder': 'Должен начитаться с http:// или https://',
                                                'size': 40}),
            "url": forms.URLInput(attrs={'placeholder': 'Должен начитаться с http:// или https://',
                                         'size': 40})
        }


class UploadFileForm(forms.Form):
    '''Форма для массового импорта объявления'''
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'zip'])])
