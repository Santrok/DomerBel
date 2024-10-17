import calendar
from datetime import datetime, timedelta, timezone

from dirtyfields import DirtyFieldsMixin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from related_data.models import Region, Category
from services.files.images import convert_image_to_avif
from services.files.uploaded_file import upload_to


class Store(DirtyFieldsMixin, models.Model):
    """
    Модель магазина
    связи: с User(FK), с Region(FK), с Category(FK)
    """
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион')
    title = models.CharField('Название магазина', max_length=60)
    slug = models.SlugField('URL', max_length=30, unique=True)
    description = models.TextField('Описание')
    contact_name = models.CharField('Контактное лицо', max_length=100)
    email = models.EmailField('E-Mail')
    phone_num = models.CharField('Номер телефона', max_length=255, blank=True, null=True)
    video_link = models.URLField('Ссылка на видеоролик YouTube', blank=True, null=True)
    logo_image = models.ImageField('Логотип', upload_to=upload_to, blank=True, null=True)
    date_of_create = models.DateTimeField('Дата создания', auto_now_add=True)
    date_of_deactivate = models.DateTimeField('Дата деактивации', blank=True, null=True)
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE, verbose_name='Пользователь, создавший магазин')
    moderated = models.BooleanField("Прошло модерацию", null=True, blank=True)
    is_active = models.BooleanField('Активный магазин', default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    url = models.URLField('Ссылка на сайт магазина', blank=True, null=True)
    address = models.CharField('Адрес', max_length=255, blank=True, null=True)
    counter_views = models.IntegerField('Счетчик просмотров', default=0)
    moderation_error_message = models.TextField("Текст причины отказа в модерации",
                                                help_text="Отправиться пользователю на Email",
                                                blank=True, null=True)
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
        """
        Сохраняет экземпляр модели Store, высчитывает дату деактивации магазина,
        конвертирует логотип в формат AVIF
        """
        day_now = datetime.now()
        if calendar.isleap(int(day_now.strftime('%Y'))) and int(day_now.strftime("%m")) <= 2:
            self.date_of_deactivate = day_now + timedelta(days=366)
        else:
            self.date_of_deactivate = day_now + timedelta(days=365)
        if self.logo_image and not self.logo_image.url.lower().endswith('avif'):
            convert_image_to_avif(photo=self.logo_image)  # Конвертация изображения в формат AVIF
        super(Store, self).save(*args, **kwargs)

    def get_days_till_expiration(self):
        """
        Возвращает количество дней до истечения срока действия магазина
        """
        days_till_expiration = self.date_of_deactivate - datetime.now(timezone.utc)
        return days_till_expiration.days

    def get_absolute_url(self):
        """
        Определяет URL-адрес, связанный с экземпляром модели.
        """
        return reverse('store_by_title', kwargs={"store_slug": self.slug})


class StoreAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Publication
    """

    @admin.display(description='')
    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.logo_image.url}' style='width=150px; height: 150px;'")

    readonly_fields = ["date_of_create", "get_html_photo"]
    fields = ["title",
              "region",
              "address",
              "category",
              "user",
              "description",
              "url",
              "slug",
              "video_link",
              "counter_views",
              ("contact_name", "phone_num", "email"),
              ("date_of_create", "date_of_deactivate"),
              ("is_active", "moderated"),
              "moderation_error_message",
              ("logo_image", "get_html_photo"),
              ]

    prepopulated_fields = {"slug": ("title",)}
    list_display = ('id', 'title', 'is_active', "moderated")
    list_display_links = ('title',)
    search_fields = ("id", 'title', 'user__email')
    list_filter = ['is_active']
    list_editable = ['is_active', "moderated"]
    list_per_page = 50
    ordering = ["-date_of_create"]

