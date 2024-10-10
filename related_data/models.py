from django.contrib.postgres.fields import ArrayField
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


# Create your models here.


class Region(MPTTModel):
    """Модель областей и городов связи:
        дерево связи в самой таблице MPТT(FK)"""
    area = models.CharField(max_length=255, verbose_name='Область, город')
    type = models.CharField(max_length=255, choices=[('Область', 'Область'), ('Город', 'Город')],
                            verbose_name='Тип местонахождения')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Отношение')
    slug = models.SlugField(unique=True, verbose_name='URL')

    class MPTTMeta:
        order_insertion_by = ('area',)

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.area


class Category(MPTTModel):
    """Модель категорий объявлений и магазинов связи:
        дерево связи в самой таблице MPТT(FK)"""
    title = models.CharField(max_length=255, verbose_name='Категория')
    type = models.CharField(max_length=255,
                            choices=[('category_1', 'category_1'), ('category_2', 'category_2'),
                                     ('category_3', 'category_3'), ('category_4', 'category_4')],
                            verbose_name='Уровень категории')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Отношение')
    fav_title = models.CharField(max_length=1000, verbose_name="Заголовок на вкладке", blank=True, null=True)
    keywords = models.CharField(max_length=3000, verbose_name="Ключевые слова", blank=True, null=True)
    keywords_description = models.CharField(max_length=3000, verbose_name="Meta описание", blank=True, null=True)
    main_title = models.CharField(max_length=1000, verbose_name="Главный заголовок", blank=True, null=True)
    slug = models.SlugField(unique=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Field(models.Model):
    """Модель хранения полей для дополнительной информации объявления по категории
        связи: Category(FK)"""
    title = models.CharField('Заголовок поля', max_length=500, blank=True, null=True)
    title_ad = models.CharField("Заголовок для администратора", max_length=500, blank=True, null=True)
    error = models.CharField('Текст ошибки при неверно введенных данных', max_length=500, blank=True, null=True)
    spisok = models.ForeignKey('Spisok', verbose_name='Связь со списком', on_delete=models.CASCADE, blank=True,
                               null=True)
    category = models.ForeignKey('Category', verbose_name='Связь с категорией', on_delete=models.CASCADE, blank=True,
                                 null=True)
    int_val_list = ArrayField(models.CharField('Список числовых значений для задания диапазонов фильтрации',
                                               max_length=1000, blank=True, null=True),
                              blank=True, null=True, default=list)
    min_val_interval_date = models.IntegerField('Минимально возможный год для выбора', blank=True, null=True)
    max_val_interval_date = models.IntegerField('Максимально возможный год для выбора', blank=True,null=True)
    search = models.CharField('Поле для поиска', max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Поле'
        verbose_name_plural = 'Поля'

    def __str__(self):
        return f"{self.title}---{self.search}"


class Spisok(models.Model):
    """Модель хранения списка значений для модели Field"""
    title = models.CharField('Заголовок списка', max_length=255)

    class Meta:
        verbose_name = 'Список элементов для полей'
        verbose_name_plural = 'Списки элементов для полей'

    def __str__(self):
        return self.title


class Element(models.Model):
    """Модель хранения значения элемента для модели Spisok.
        связи: Spisok(FK)"""
    title = models.CharField('Заголовок элемента', max_length=255)
    spisok = models.ForeignKey('Spisok', verbose_name='Связь со списком', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Элемент для списка'
        verbose_name_plural = 'Элементы для списка'

    def __str__(self):
        return self.title


class ElementTwo(models.Model):
    """Модель хранения расширенного значения элемента для модели Element.
        связи: Element(FK)"""
    title = models.CharField('Загловок второго элемента', max_length=255)
    element = models.ForeignKey('Element', verbose_name='Связь с элементом', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Дополнительный элемент для списка'
        verbose_name_plural = 'Дополнительные элементы для списка'

    def __str__(self):
        return self.title
