from functools import partial
from itertools import groupby
from operator import attrgetter
from string import Template

from django import forms
from django.forms import ClearableFileInput
from django.forms.models import ModelChoiceIterator, ModelChoiceField
from django.utils.safestring import mark_safe
from mptt.forms import TreeNodeChoiceField

from advertisement.models import Region, Category, Store

from users.validators import validate_phone
from django.core.validators import FileExtensionValidator


class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        if value:
            html = Template(f'{input_html}<div class="photo_img"><div class="delete_img"></div><img src="$link"/></div>')
            img_html = mark_safe(html.substitute(link=value.url))
            return img_html
        return input_html


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(ModelChoiceField):
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)


class StoreForm(forms.ModelForm):
    region = forms.ModelChoiceField(queryset=Region.objects.filter(type="Город"),
                                    label="Регион, город, область",
                                    widget=forms.Select(attrs={'class': 'input_field'}))
    address = forms.CharField(max_length=255,
                              required=False,
                              label="Адрес",
                              widget=forms.TextInput(attrs={'class': 'input_field'}))
    category = GroupedModelChoiceField(queryset=Category.objects.filter(level=1).prefetch_related('parent'),
                                       choices_groupby='parent',
                                       label="Раздел",
                                       widget=forms.Select(attrs={'size': 10}), empty_label=None)
    title = forms.CharField(max_length=255,
                            required=True,
                            label="Название магазина",
                            widget=forms.TextInput(attrs={'class': 'input_field'}))
    slug = forms.SlugField(min_length=4,
                           max_length=20,
                           required=True,
                           label="Имя магазина, которое будет отображаться в URL-e страницы Вашего магазина "
                                 "(только латинские буквы и тире, должно начинаться с буквы и содержать от 4 до 20 символов",
                           widget=forms.TextInput(attrs={'class': 'input_field'}))
    description = forms.CharField(required=True,
                                  label="Описание",
                                  widget=forms.Textarea(attrs={'class': 'input_field'}))
    url = forms.URLField(required=False,
                         label="Сайт магазина",
                         widget=forms.URLInput(attrs={'class': 'input_field',
                                                      'placeholder': 'Должен начитаться с http:// или https://',
                                                      'size': 40}))
    contact_name = forms.CharField(required=True, max_length=255,
                                   label="Контактное лицо",
                                   widget=forms.TextInput(attrs={'class': 'input_field'}))
    email = forms.EmailField(required=True,
                             label="E-mail",
                             widget=forms.TextInput(attrs={'class': 'input_field', 'id': 'store_email'}))
    phone_num = forms.CharField(max_length=255,
                                required=False,
                                label="Телефон",
                                widget=forms.TextInput(attrs={'class': 'input_field'}),
                                validators=[validate_phone])
    video_link = forms.URLField(required=False,
                                label="Ссылка на видеоролик YouTube",
                                widget=forms.URLInput(attrs={'class': 'input_field',
                                                             'placeholder': 'Должен начитаться с http:// или https://',
                                                             'size': 40}))
    logo_image = forms.ImageField(required=True,
                                  label="Логотип",
                                  widget=ImagePreviewWidget(attrs={'class': 'input_field', "id": "id_logo_image"}))

    class Meta:
        model = Store
        fields = ['region', 'address', 'category', 'title', 'slug', 'description', 'url', 'contact_name', 'email',
                  'phone_num', 'video_link', 'logo_image']


class UploadFileForm(forms.Form):
    '''Форма для массового импорта объявления'''
    file = forms.FileField( validators = [FileExtensionValidator(allowed_extensions=['xlsx','zip'])])