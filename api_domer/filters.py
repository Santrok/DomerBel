from django_filters import FilterSet, DateTimeFilter

from main_page_domer.models import Publication


class PublicationsFilter(FilterSet):
    date_published = DateTimeFilter(
        field_name='date_of_create',
        lookup_expr='date',
        label='Дата публикации (дд-мм-гггг)',
        input_formats=['%d-%m-%Y']
    )

    class Meta:
        model = Publication
        fields = ['date_of_create']
