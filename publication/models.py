from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field

from services.files.images import convert_image_to_avif
from services.files.uploaded_file import upload_to
from utils.slug_generator import unique_slugify


# Create your models here.


class Publication(models.Model):
    """
    Модель публикации
    связи: с User(FK)
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("URL", max_length=255, unique=True)
    announcement = CKEditor5Field('Аннотация', config_name='extends')
    description = CKEditor5Field('Текст статьи', config_name='extends')
    preview_image = models.ImageField("Фото", upload_to=upload_to)
    date_of_create = models.DateTimeField("Дата создания", auto_now_add=True)
    counter_views = models.IntegerField("Счетчик просмотров", default=0)
    moderated = models.BooleanField("Прошло модерацию", default=False)
    search_vector = SearchVectorField(null=True, editable=False)
    search_title_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        indexes = [
            GinIndex(fields=['search_vector']),
            GinIndex(fields=['search_title_vector']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('publication_by_slug', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """
        Сохраняет экземпляр модели Publication, конвертирует логотип в формат AVIF, формирует поле slug,
        выполняет индексацию по полям 'title' и 'description' для полнотекстового поиска
        """
        if self.preview_image and not self.preview_image.url.lower().endswith('avif'):
            convert_image_to_avif(photo=self.preview_image)  # Конвертация изображения в формат AVIF
        self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
        self.search_vector = SearchVector('title', 'description', 'announcement')
        self.search_title_vector = SearchVector('title')
        super(Publication, self).save(*args, **kwargs)


class PublicationAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Publication
    """

    @admin.display(description='')
    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.preview_image.url}' style='width=150px; height: 150px;'")

    readonly_fields = ["date_of_create", "get_html_photo"]
    fields = ["user",
              "title",
              "announcement",
              "description",
              "slug",
              "counter_views",
              "date_of_create",
              "moderated",
              ("preview_image", "get_html_photo"),
              ]

    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'moderated')
    list_display_links = ('title',)
    search_fields = ('title', 'user__email')
    list_filter = ['moderated']
    list_editable = ['moderated']
    list_per_page = 50
