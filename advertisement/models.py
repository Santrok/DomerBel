import calendar
from datetime import datetime, timedelta, timezone

import PIL
from dirtyfields import DirtyFieldsMixin
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass, BrinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector

from django.db import models
from django.db.models.functions import Upper

from django.urls import reverse
from django.utils.timezone import make_aware
from mptt.models import MPTTModel, TreeForeignKey

from django.conf import settings

from .utils_for_models import add_watermark_to_photo, upload_to, unique_slugify
from users.validators import validate_phone
from .validators import validate_words


class PhotoAdvertisement(models.Model):
    photo = models.ImageField(upload_to=upload_to, verbose_name='Фото', blank=True, null=True)
    advertisement = models.ForeignKey('Advertisement', on_delete=models.CASCADE, verbose_name='Фотография')

    class Meta:
        verbose_name = 'Фото объявления'
        verbose_name_plural = 'Фото объявлений'

    def __str__(self):
        return f'{self.advertisement.id}-{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        photo = add_watermark_to_photo(self.photo.path)
        photo.save(self.photo.path, "WebP")


class Advertisement(DirtyFieldsMixin, models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    article = models.CharField(max_length=255, blank=True, null=True, verbose_name="Артикул")
    title = models.CharField(max_length=255, verbose_name='Заголовок', db_index=True, validators=[validate_words])
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0, verbose_name='Цена')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Раздел')
    bearer = models.CharField(max_length=50, choices=[('Частное лицо', 'Частное лицо'), ('Компания', 'Компания')],
                              verbose_name='Податель', default='Частное лицо')
    region = models.ForeignKey('Region', on_delete=models.CASCADE, verbose_name='Регион, город, район')
    preview_image = models.ImageField(upload_to=upload_to, verbose_name='Главная фотография',
                                      blank=True, null=True)
    counter_views = models.IntegerField(default=0, verbose_name='Счетчик просмотров')
    contact_name = models.CharField(max_length=255, verbose_name='Контактное лицо',validators=[validate_words])
    phone_num = models.CharField(max_length=255, verbose_name='Телефон', validators=[validate_phone])
    email = models.EmailField(verbose_name='E-Mail')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Магазин")
    slug = models.SlugField(unique=True, blank=True, verbose_name='URL', max_length=500)
    date_of_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания объявления')
    date_of_change = models.DateTimeField(auto_now=True, verbose_name='Дата изменения объявления')
    date_of_deactivate = models.DateTimeField(blank=True, null=True, verbose_name='Дата деактивации объявления')
    moderated = models.BooleanField(default=False, verbose_name='Прошло модерацию')
    is_active = models.BooleanField(default=False, verbose_name='Объявление активно')
    vip = models.BooleanField(default=False, verbose_name="Сделать VIP-объявлением")
    highlight_ad = models.BooleanField(default=False, verbose_name="Выделить объявление")
    special_accommodation = models.BooleanField(default=False, verbose_name="Спецразмещение")
    raise_in_search = models.BooleanField(default=False, verbose_name="Поднять в поиске")
    additional_information = models.JSONField()
    additional_information_view = ArrayField(ArrayField(models.CharField(max_length=500)), blank=True, null=True, editable=False)
    description = models.TextField(verbose_name='Описание',validators=[validate_words])
    video_link = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')  # хранит строку, которая представляет валидный URL-адрес
    search_vector = SearchVectorField(null=True, editable=False)
    search_title_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        indexes = [
            GinIndex(fields=['search_vector']),
            GinIndex(fields=['search_title_vector']),
            GinIndex(fields=['title'], name='title_gin_index',
                     opclasses=['gin_trgm_ops']),
            GinIndex(OpClass(Upper('title'), name='gin_trgm_ops'),
                     name='title_upper_gin_index'),
            BrinIndex(fields=['date_of_create']),
        ]

    def __str__(self):
        return self.title

    def get_days_till_expiration(self):
        days_till_expiration = self.date_of_deactivate - datetime.now(timezone.utc)
        return days_till_expiration.days

    def get_absolute_url(self):
        return reverse('advertisement_details', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if 'additional_information' in self.get_dirty_fields():
            self.additional_information_view = list(self.additional_information.items())
        self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
        self.date_of_deactivate = self.date_of_create + timedelta(days=60)
        self.search_vector = SearchVector('title', 'description')
        self.search_title_vector = SearchVector('title')
        super().save(*args, **kwargs)
        if self.preview_image:
            try:
                photo = add_watermark_to_photo(self.preview_image.path)
                photo.save(self.preview_image.path, "WebP")
            except FileNotFoundError:
                self.preview_image = None
            except PIL.UnidentifiedImageError:
                self.preview_image = None
            finally:
                super(Advertisement, self).save(*args, **kwargs)


class Category(MPTTModel):
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

    def get_absolute_url(self): # для карты сайта sitemap.xml
        return "/people/%i/" % self.id


class Region(MPTTModel):
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


class Field(models.Model):
    title = models.CharField(max_length=500, verbose_name='Заголовок поля', blank=True, null=True)
    title_ad = models.CharField(max_length=500, blank=True, null=True)
    error = models.CharField(max_length=500, verbose_name='Текст ошибки при неверно введенных данных', blank=True, null=True)
    spisok = models.ForeignKey('Spisok', on_delete=models.CASCADE, verbose_name='Связь со списком', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Связь с категорией', blank=True, null=True)
    int_val_list = ArrayField(models.CharField(max_length=1000, blank=True, null=True, verbose_name='Список числовых значений для задания диапазонов фильтрации'), blank=True, null=True, default=list)
    min_val_interval_date = models.IntegerField(verbose_name='Минимально возможный год для выбора', blank=True, null=True)
    max_val_interval_date = models.IntegerField(verbose_name='Максимально возможный год для выбора', blank=True, null=True)
    search = models.CharField(max_length=500, blank=True, null=True)


    class Meta:
        verbose_name = 'Поле'
        verbose_name_plural = 'Поля'

    def __str__(self):
        return f"{self.title}---{self.search}"


class Spisok(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок списка')

    class Meta:
        verbose_name = 'Список элементов для полей'
        verbose_name_plural = 'Списки элементов для полей'

    def __str__(self):
        return self.title


class Element(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок элемента')
    spisok = models.ForeignKey('Spisok', on_delete=models.CASCADE, verbose_name='Связь со списком')

    class Meta:
        verbose_name = 'Элемент для списка'
        verbose_name_plural = 'Элементы для списка'

    def __str__(self):
        return self.title


class ElementTwo(models.Model):
    title = models.CharField(max_length=255, verbose_name='Загловок второго элемента')
    element = models.ForeignKey('Element', on_delete=models.CASCADE, verbose_name='Связь с элементом')

    class Meta:
        verbose_name = 'Дополнительный элемент для списка'
        verbose_name_plural = 'Дополнительные элементы для списка'

    def __str__(self):
        return self.title


class Store(models.Model):
    region = models.ForeignKey('Region', on_delete=models.CASCADE, verbose_name='Регион')
    title = models.CharField(max_length=60,verbose_name='Название магазина')
    slug = models.SlugField(max_length=30, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')
    contact_name = models.CharField(max_length=100, verbose_name='Контактное лицо')
    email = models.EmailField(verbose_name='E-Mail')
    phone_num = models.CharField(max_length=255, blank=True, null=True, verbose_name='Номер телефона')
    video_link = models.URLField(blank=True, null=True, verbose_name='Ссылка на YouTube видео')  # хранит строку, которая представляет валидный URL-адрес
    logo_image = models.ImageField(upload_to='images/store_img', default='default/no_image.jpg', blank=True, null=True, verbose_name='Логотип')
    date_of_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_deactivate = models.DateTimeField(blank=True, null=True, verbose_name='Дата деактивации')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, verbose_name='Пользователь, создавший магазин')
    is_active = models.BooleanField(default=False, verbose_name='Активный магазин')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')
    url = models.URLField(blank=True, null=True, verbose_name='Ссылка на сайт магазина')  # хранит строку, которая представляет валидный URL-адрес
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Адрес')
    counter_views = models.IntegerField(default=0, verbose_name='Счетчик просмотров')
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        day_now = datetime.now()
        if calendar.isleap(int(day_now.strftime('%Y'))) and int(day_now.strftime("%m")) <= 2:
            self.date_of_deactivate = day_now + timedelta(days=366)
        else:
            self.date_of_deactivate = day_now + timedelta(days=365)
        super().save(*args, **kwargs)
        self.search_vector = SearchVector('title', 'description')
        super(Store, self).save(*args, **kwargs)

    def get_days_till_expiration(self):
        days_till_expiration = self.date_of_deactivate - datetime.now(timezone.utc)
        return days_till_expiration.days


class UploadFile(models.Model):
    '''Модель для сохранения файла для массового импорта объявлений'''
    def get(instance,filename):
        '''Ф-ция, возращает путь, по которому хранитьс файл для массого импорта объявлений'''
        return f'files_for_bulk_import_of_ads/{instance.user.email}/{filename}'

    time_upload_file = models.DateTimeField(auto_now_add=True, verbose_name='Время загрузки файла')
    file = models.FileField(upload_to=get, verbose_name='Путь к файлу с объявлениями')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'

    def __str__(self):
        return f'{self.user}_{self.time_upload_file}'

class ErrorFile(models.Model):
    '''Модель, возвращающая путь, по которому храниться файл с ошибками после массового импорта объялений'''
    def get(instance,filename):
        '''Ф-ция, возвращает путь, по которому храниться файл для массого импорта объявлений'''

        return f'files_for_bulk_import_of_ads/{instance.user.email}/{filename}'

    time_upload_file = models.DateTimeField(auto_now_add=True, verbose_name='Время создания файла')
    file = models.CharField(max_length=255, verbose_name='Путь к файлу с объявлениями с ошибками')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.BooleanField(default=False, verbose_name='Был доступ у пользователя к файлу или нет')

    class Meta:
        verbose_name = 'Файл с объявлениями с ошибками'
        verbose_name_plural = 'Файлы с объявлениями с ошибками'

    def __str__(self):
        return f'{self.user}_{self.time_upload_file}'


class BadWords(models.Model):
    '''Модель для валидации нецензурных слов'''
    word = models.CharField(max_length=255)

    def __str__(self):
        return self.word[0:2]+'*'*(len(self.word)-3)+self.word[-1]

    class Meta:
        verbose_name = 'Нецензурное слово'
        verbose_name_plural = 'Нецензурные слова'