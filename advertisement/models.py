from datetime import datetime, timedelta, timezone
import logging

import PIL
from dirtyfields import DirtyFieldsMixin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass, BrinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models.functions import Upper
from django.urls import reverse
from django.utils.safestring import mark_safe

from related_data.models import Category, Region
from services.files.images import convert_image_to_avif, add_watermark_to_image
from services.files.uploaded_file import upload_to
from store.models import Store
from utils.slug_generator import unique_slugify
from utils.validators import validate_words, validate_phone

#настрока логирования
logger = logging.getLogger('advertisement')


class PhotoAdvertisement(models.Model):
    """
    Модель дополнительного изображения объявления
    связи: с Advertisement(FK)
    """
    photo = models.ImageField("Фотография", upload_to=upload_to, blank=True, null=True)
    advertisement = models.ForeignKey('Advertisement', verbose_name="Объявление", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Фото объявления"
        verbose_name_plural = "Фото объявлений"

    def __str__(self):
        return f'Объявление {self.advertisement.id}-{self.id}'

    def save(self, *args, **kwargs):
        """
        Конвертирует изображение в AVIF формат
        и добавляет водяной знак на изображение,
        и сохраняет экземпляр модели
        """
        if self.photo and not self.photo.url.lower().endswith('avif'):
            convert_image_to_avif(photo=self.photo)
        super().save(*args, **kwargs)

        # Добавление водяного знака
        photo = add_watermark_to_image(self.photo.path)
        photo.save(self.photo.path, "avif")


class PhotoAdvertisementAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: PhotoAdvertisement
    """

    @admin.display(description='')
    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.photo.url}' style='width=100px; height: 100px;'>")

    readonly_fields = ['get_html_photo']
    fields = [("photo", "get_html_photo")]


class Advertisement(DirtyFieldsMixin, models.Model):
    """
    Модель хранения информации об объявлении
    связи: с User(FK), с Region(FK), с Category(FK), Store(FK)
    """
    author = models.ForeignKey(get_user_model(), verbose_name="Автор", on_delete=models.CASCADE, blank=True, null=True)
    article = models.CharField("Артикул", max_length=255, blank=True, null=True)
    title = models.CharField("Заголовок", max_length=255, db_index=True, validators=[validate_words])
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Раздел')
    bearer = models.CharField('Податель',
                              max_length=50,
                              choices=[('Частное лицо', 'Частное лицо'), ('Компания', 'Компания')],
                              default='Частное лицо')
    region = models.ForeignKey(Region, verbose_name='Регион, город, район', on_delete=models.CASCADE)
    preview_image = models.ImageField("Главная фотография", upload_to=upload_to,
                                      blank=True, null=True, default=None)
    additional_information = models.JSONField("Дополнительная информация")
    contact_name = models.CharField("Контактное лицо", max_length=255, validators=[validate_words])
    phone_num = models.CharField("Телефон", max_length=255, validators=[validate_phone])
    email = models.EmailField("E-Mail")
    description = models.TextField("Описание", validators=[validate_words])
    video_link = models.URLField("Ссылка на видео", blank=True, null=True, default=None)
    store = models.ForeignKey(Store, verbose_name="Магазин", on_delete=models.CASCADE, blank=True, null=True)
    counter_views = models.IntegerField("Счетчик просмотров", default=0)
    slug = models.SlugField("URL", unique=True, blank=True, max_length=500)
    date_of_create = models.DateTimeField("Дата создания объявления", auto_now_add=True)
    date_of_last_activation = models.DateTimeField("Дата последней активации объявления",
                                                   blank=True,
                                                   null=True)
    date_of_delete = models.DateTimeField("Дата удаления объявления", blank=True, null=True)
    date_of_deactivate = models.DateTimeField("Дата деактивации объявления", blank=True, null=True)
    vip = models.BooleanField("Сделать VIP-объявлением", default=False)
    shown_vip = models.BooleanField("Показано на главной странице", default=False)
    shown_vip_count = models.IntegerField("Счетчик показов на главной странице", default=0)
    shown_vip_category = models.BooleanField("Показано на странице категории", default=False)
    shown_vip_category_count = models.IntegerField("Счетчик показов на странице категории", default=0)
    date_of_deactivate_vip = models.DateTimeField("Дата деактивации VIP", blank=True, null=True)
    highlight_ad = models.BooleanField("Выделить объявление", default=False)
    date_of_deactivate_highlight_ad = models.DateTimeField("Дата деактивации выделения", blank=True, null=True)
    special_accommodation = models.BooleanField("Спецразмещение", default=False)
    date_of_deactivate_special_accommodation = models.DateTimeField("Дата деактивации спецразмещения",
                                                                    blank=True,
                                                                    null=True)
    raise_in_search = models.BooleanField("Поднять в поиске", default=False)
    search_boost_date = models.DateTimeField("Дата поднятия в поиске", blank=True, null=True)
    moderated = models.BooleanField("Прошло модерацию", null=True, blank=True)
    is_active = models.BooleanField("Объявление активно", default=False)
    additional_information_view = ArrayField(ArrayField(models.CharField(max_length=500)), blank=True, null=True,
                                             editable=False)
    moderation_error_message = models.TextField("Текст причины отказа в модерации",
                                                help_text="Отправиться пользователю на Email",
                                                blank=True, null=True)
    search_vector = SearchVectorField(null=True, editable=False)
    search_title_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Oбъявление"
        verbose_name_plural = "Oбъявления"
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(fields=["search_title_vector"]),
            GinIndex(fields=["title"], name="title_gin_index",
                     opclasses=["gin_trgm_ops"]),
            GinIndex(OpClass(Upper('title'), name="gin_trgm_ops"),
                     name="title_upper_gin_index"),
            BrinIndex(fields=["date_of_create"]),
        ]

    def __str__(self):
        return self.title

    def get_days_till_expiration(self):
        """
        Возвращает количество дней до деактивации объявления
        """
        days_till_expiration = self.date_of_deactivate - datetime.now(timezone.utc)
        return days_till_expiration.days

    def get_absolute_url(self):
        return reverse('advertisement_details', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """
        Конвертирует изображение в AVIF формат, добавляет водяной знак на изображение,
        заполняет поля даты деактивации, удаления, и последнего поднятия объявления,
        заполняет поля slug, и additional_information_view и сохраняет экземпляр модели
        """
        if "additional_information" in self.get_dirty_fields():
            self.additional_information_view = list(self.additional_information.items())

        self.slug = unique_slugify(self, self.title)

        if not self.date_of_deactivate and not self.date_of_delete:
            self.date_of_deactivate = datetime.now(timezone.utc) + timedelta(days=60)
            self.date_of_delete = datetime.now(timezone.utc) + timedelta(days=180)
            self.search_boost_date = datetime.now(timezone.utc)
            self.date_of_last_activation = datetime.now(timezone.utc)

        if self.video_link == "":
            self.video_link = None

        if self.preview_image and not self.preview_image.url.lower().endswith('avif'):
            convert_image_to_avif(photo=self.preview_image)  # Конвертация изображения в формат AVIF

        if self.preview_image and "preview_image" in self.get_dirty_fields():
            try:
                photo = add_watermark_to_image(self.preview_image.path)
                photo.save(self.preview_image.path, "avif", save=False)
            except FileNotFoundError:
                self.preview_image = None
            except PIL.UnidentifiedImageError:
                self.preview_image = None
            except Exception as e:
                logger.warning(f'Ошибка при сохранении объявления: {str(e)}', exc_info=True)

        super().save(*args, **kwargs)


class PhotoAdvertisementInlines(admin.StackedInline):
    """
    Класс управления отображения PhotoAdvertisement в админ панели редактирования сущности Advertisement
    """

    @admin.display(description='')
    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.photo.url}' style='width=150px; height: 150px;'>")

    readonly_fields = ['get_html_photo']
    fields = [("photo", "get_html_photo")]
    model = PhotoAdvertisement
    max_num = 30
    extra = 1


class AdvertisementAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Advertisement
    """

    @admin.display(description='')
    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.preview_image.url}' style='width=150px; height: 150px;'")

    readonly_fields = ["date_of_create", "get_html_photo", "search_boost_date"]
    fields = ["title",
              "region",
              "category",
              "author",
              "price",
              "additional_information",
              "description",
              "bearer",
              "article",
              "store",
              "slug",
              "video_link",
              "counter_views",
              ("contact_name", "phone_num", "email"),
              ("date_of_create", "date_of_last_activation", "date_of_deactivate", "date_of_delete"),
              ("vip", "date_of_deactivate_vip"),
              ("highlight_ad", "date_of_deactivate_highlight_ad"),
              ("special_accommodation", "date_of_deactivate_special_accommodation"),
              ("raise_in_search", "search_boost_date"),
              ("is_active", "moderated"),
              "moderation_error_message",
              ("preview_image", "get_html_photo"),
              ]

    prepopulated_fields = {"slug": ("title",)}
    list_display = ('id',
                    'title',
                    'moderated',
                    'is_active',
                    'vip',
                    'highlight_ad',
                    'special_accommodation',
                    )
    list_display_links = ('title',)
    search_fields = ('title', 'author__email', 'id')
    list_filter = ('moderated',
                   'is_active',
                   'vip',
                   'highlight_ad',
                   'special_accommodation',
                   )
    list_editable = ['moderated',
                     'is_active',
                     ]
    ordering = ['-date_of_last_activation']
    list_per_page = 50
    inlines = [PhotoAdvertisementInlines]


class UploadFile(models.Model):
    """
    Модель для сохранения файла для массового импорта объявлений,
    связи: с User(FK)
    """

    def get(instance, filename):
        """
        Возвращает путь, по которому храниться файл с объявлениями для массового импорта
        """
        return f'files_for_bulk_import_of_ads/{instance.user.email}/{filename}'

    time_upload_file = models.DateTimeField("Время загрузки файла", auto_now_add=True)
    file = models.FileField("Путь к файлу с объявлениями", upload_to=get)
    user = models.ForeignKey(get_user_model(), verbose_name="Пользователь", on_delete=models.CASCADE)
    status = models.BooleanField("Статус обработки файла", default=False)

    class Meta:
        verbose_name = "Загруженный файл с объявлениями для массового импорта"
        verbose_name_plural = "Загруженные файлы с объявлениями для массового импорта"

    def __str__(self):
        return f'{self.user}_{self.time_upload_file}'


class UploadFileAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: UploadFile
    """
    pass


class ErrorFile(models.Model):
    """
    Модель, хранящая путь, по которому храниться
    файл с ошибками после массового импорта объявлений,
    связи: с User(FK), UploadFile(O2O)
    """
    time_upload_file = models.DateTimeField("Время создания файла", auto_now_add=True)
    file = models.CharField("Путь к файлу с объявлениями с ошибками", max_length=255)
    user = models.ForeignKey(get_user_model(), verbose_name="Пользователь", on_delete=models.CASCADE)
    upload_file = models.OneToOneField(UploadFile,
                                       verbose_name="Загруженный файл",
                                       on_delete=models.CASCADE,
                                       blank=True,
                                       null=True)

    class Meta:
        verbose_name = "Файл с ошибками объявлений при массовом импорте"
        verbose_name_plural = "Файлы с ошибками объявлений при массовом импорте"

    def __str__(self):
        return f'{self.user}_{self.time_upload_file}'


class ErrorFileAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: ErrorFile
    """
    pass


class Complaint(models.Model):
    """
    Модель, хранящая жалобы на объявления,
    связи: с Advertisement(FK), ReasonOfComplaint(FK)
    """
    reason = models.ForeignKey('ReasonOfComplaint', verbose_name="Причина жалобы", on_delete=models.CASCADE)
    text = models.TextField("Обоснование жалобы")
    date = models.DateTimeField("Дата создания жалобы", auto_now_add=True)
    user = models.CharField("Пользователь, отправивший жалобу", max_length=500)
    advertisement = models.ForeignKey(Advertisement,
                                      verbose_name="Объявление, на которое пожаловались",
                                      on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Жалоба на объявление"
        verbose_name_plural = "Жалобы на объявления"

    def __str__(self):
        return self.reason


class ComplaintAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Complaint
    """
    pass


class ReasonOfComplaint(models.Model):
    """
    Модель, хранящая причины жалобы
    """
    reason = models.CharField("Причина жалобы", max_length=1000)

    class Meta:
        verbose_name = 'Причина жалобы'
        verbose_name_plural = 'Причины жалобы'
        ordering = ['id']

    def __str__(self):
        return self.reason


class ReasonOfComplaintAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: ReasonOfComplaint
    """
    pass
