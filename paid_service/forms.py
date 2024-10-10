from django import forms
from django.forms import BoundField
from django.forms.boundfield import BoundWidget
from django.utils.functional import cached_property

from advertisement.models import Advertisement
from .models import Service


class CustomBoundWidget(BoundWidget):
    """Добавляет к базовому виджету два метода
        которые возвращают стоимость и период действия"""
    @property
    def get_cost(self):
        return self.data["cost"]

    @property
    def get_validity_period(self):
        return self.data["validity_period"]


class CustomBoundField(BoundField):
    """Переопределен для использования кастомного виджета вместо базового"""
    @cached_property
    def subwidgets(self):
        id_ = self.field.widget.attrs.get("id") or self.auto_id
        attrs = {"id": id_} if id_ else {}
        attrs = self.build_widget_attrs(attrs)
        return [
            CustomBoundWidget(self.field.widget, widget, self.form.renderer)
            for widget in self.field.widget.subwidgets(
                self.html_name, self.value(), attrs=attrs
            )
        ]


class PaidMultipleCheckbox(forms.CheckboxSelectMultiple):
    """Добавляет значения стоимости и срока действия
        в дополнение к базовым атрибутам"""
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        option_attrs = (
            self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        )
        if selected:
            option_attrs.update(self.checked_attribute)
        if "id" in option_attrs:
            option_attrs["id"] = self.id_for_label(option_attrs["id"], index)
        cost = value.instance.cost
        option_attrs["data-cost"] = cost
        validity_period = value.instance.validity_period
        return {
            "name": name,
            "value": value,
            "label": label,
            "selected": selected,
            "index": index,
            "attrs": option_attrs,
            "type": self.input_type,
            "template_name": self.option_template_name,
            "wrap_label": True,
            "cost": cost,
            "validity_period": validity_period,
        }


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Переопределен для использования кастомного поля вместо базового"""
    def get_bound_field(self, form, field_name):
        return CustomBoundField(form, self, field_name)


class PaidForm(forms.Form):
    advertisement = forms.ModelChoiceField(queryset=Advertisement.objects.all(), widget=forms.HiddenInput)
    services = CustomModelMultipleChoiceField(queryset=Service.objects.all(), widget=PaidMultipleCheckbox, label='')
