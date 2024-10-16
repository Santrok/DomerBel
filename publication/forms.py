from django import forms
from string import Template
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from publication.models import Publication


class ImagePreviewWidget(forms.widgets.FileInput):
    """
    Переопределение метода render для отображения загруженного изображения
    """
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        if value:
            html = Template(f"""{input_html}<div class="photo_img">
                                            <div class="delete_img"></div>
                                            <img src="$link"/>
                                            </div>""")
            img_html = mark_safe(html.substitute(link=value.url))
            return img_html
        return input_html


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'announcement', 'description', 'preview_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['announcement'].widget = CKEditor5Widget(config_name='extends2')
        self.fields['preview_image'].widget = ImagePreviewWidget()
        self.fields['preview_image'].widget.attrs.update({"id": "id_logo_image"})
        self.fields['announcement'].required = False
        self.fields['description'].required = False
