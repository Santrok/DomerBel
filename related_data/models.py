from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from mptt.admin import DraggableMPTTAdmin
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


# Create your models here.


class Region(MPTTModel):
    """
    Модель областей и городов
    связи: дерево связи в самой таблице MPТT(FK)
    """
    area = models.CharField(max_length=255, verbose_name='Область, город')
    type = models.CharField(max_length=255, choices=[('Область', 'Область'), ('Город', 'Город')],
                            verbose_name='Тип местонахождения')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            verbose_name='Отношение к области')
    slug = models.SlugField(unique=True, verbose_name='URL')

    class MPTTMeta:
        order_insertion_by = ('area',)

    class Meta:
        verbose_name = 'Pегион'
        verbose_name_plural = 'Pегионы'

    def __str__(self):
        return self.area


class RegionAdmin(DraggableMPTTAdmin):
    """
    Класс управления отображения в админ панели сущности: Region
    """
    prepopulated_fields = {"slug": ("area",)}
    mptt_level_indent = 30
    max_level_indent = 1

    def get_queryset(self, request):
        """
        Ограничивает уровень вложенности каждого региона
        """
        qs = super().get_queryset(request)
        return qs.filter(level__lte=self.max_level_indent)


class ElementTwo(models.Model):
    """
    Модель хранения расширенного значения элемента для модели Element
    связи: Element(FK)
    """
    title = models.CharField('Загловок второго элемента', max_length=255)
    element = models.ForeignKey('Element', verbose_name='Связь с элементом', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Дополнительное значение элемента для списка'
        verbose_name_plural = 'Дополнительные значения элементов для списка'

    def __str__(self):
        return self.title


class ElementTwoAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: ElementTwo
    """
    pass


class ElementTwoInlines(admin.StackedInline):
    """
    Класс управления отображения модели ElementTwo в админ панели редактирования сущности Element
    """
    model = ElementTwo
    extra = 0


class Element(models.Model):
    """
    Модель хранения значения элемента для модели Spisok.
    связи: Spisok(FK)
    """
    title = models.CharField('Заголовок элемента', max_length=255)
    spisok = models.ForeignKey('Spisok', verbose_name='Связь со списком', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Элемент для списка'
        verbose_name_plural = 'Элементы для списка'
        ordering = ['title']

    def __str__(self):
        return self.title


class ElementAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Element
    """
    inlines = [ElementTwoInlines]
    search_fields = ['title']


class ElementInlines(admin.StackedInline):
    """
    Класс управления отображения модели Element в админ панели редактирования сущности Spisok
    """
    model = Element
    extra = 0
    show_change_link = True


class Field(models.Model):
    """
    Модель хранения полей для дополнительной информации объявления по категории
    связи: Category(FK)
    """
    title = models.CharField('Заголовок поля', max_length=500, blank=True, null=True)
    title_ad = models.CharField("Заголовок для администратора", max_length=500, blank=True, null=True)
    error = models.CharField('Текст ошибки при неверно введенных данных', max_length=500, blank=True, null=True)
    spisok = models.ForeignKey('Spisok', verbose_name='Связь со списком', on_delete=models.CASCADE, blank=True,
                               null=True)
    category = models.ForeignKey('Category', verbose_name='Связь с категорией', on_delete=models.CASCADE, blank=True,
                                 null=True)
    int_val_list = ArrayField(models.CharField(max_length=1000, blank=True, null=True),
                              verbose_name='Список числовых значений для задания диапазонов фильтрации',
                              blank=True, null=True, default=list,
                              help_text="Укажите значения через запятую, прим. 100,200,300")
    min_val_interval_date = models.IntegerField('Минимально возможный год для выбора', blank=True, null=True)
    max_val_interval_date = models.IntegerField('Максимально возможный год для выбора', blank=True, null=True)
    search = models.CharField('Поле для поиска', max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Поле дополнительной информации объявления по категории'
        verbose_name_plural = 'Поля дополнительной информации объявления по категории'

    def __str__(self):
        return f"{self.title if self.title else self.title_ad}"


class FieldAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Field
    """

    list_display = ['__str__', 'spisok']
    list_display_links = ['__str__']
    ordering = ['title_ad']
    search_fields = ["title", "title_ad"]


class FieldInlines(admin.StackedInline):
    """
    Класс управления отображения модели Field в админ панели редактирования сущности Spisok
    """
    model = Field
    max_num = 30
    extra = 0
    show_change_link = True
    fields = ['title']


class Spisok(models.Model):
    """
    Модель хранения списка значений для модели Field
    """
    title = models.CharField('Заголовок списка', max_length=255)

    class Meta:
        verbose_name = 'Список элементов для полей'
        verbose_name_plural = 'Списки элементов для полей'

    def __str__(self):
        return self.title


class SpisokAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Spisok
    """
    inlines = [ElementInlines]
    search_fields = ['field__title', 'title']


class Category(MPTTModel):
    """
    Модель категорий объявлений и магазинов
    связи: дерево связи в самой таблице MPТT(FK)
    """
    title = models.CharField(max_length=255, verbose_name='Категория')
    type = models.CharField(max_length=255,
                            choices=[('category_1', 'Уровень 1'), ('category_2', 'Уровень 2'),
                                     ('category_3', 'Уровень 3'), ('category_4', 'Уровень 4')],
                            verbose_name='Уровень категории')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            verbose_name='Отношение к категории')
    fav_title = models.CharField(max_length=1000, verbose_name="Заголовок на вкладке", blank=True, null=True)
    keywords = models.CharField(max_length=3000, verbose_name="Ключевые слова", blank=True, null=True)
    keywords_description = models.CharField(max_length=3000, verbose_name="Meta описание", blank=True, null=True)
    main_title = models.CharField(max_length=1000, verbose_name="Главный заголовок", blank=True, null=True)
    slug = models.SlugField(unique=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Kатегория'
        verbose_name_plural = 'Kатегории'

    def __str__(self):
        return self.title


class CategoryAdmin(DraggableMPTTAdmin):
    """
    Класс управления отображения в админ панели сущности: Category
    """
    inlines = [FieldInlines]
    prepopulated_fields = {"slug": ("title",)}
    mptt_level_indent = 30
    max_level_indent = 3

    def get_queryset(self, request):
        """
        Ограничивает уровень вложенности каждой категории
        """
        qs = super().get_queryset(request)
        return qs.filter(level__lte=self.max_level_indent)
