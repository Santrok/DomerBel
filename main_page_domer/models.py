from django.urls import reverse
from django.contrib import admin
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from advertisement.models import Advertisement
from advertisement.utils_for_models import unique_slugify
from users.models import User


class Comment(models.Model):
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, verbose_name="Связь с объявлением"
    )
    comment = models.TextField(verbose_name="Текст комментария")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор"
    )
    date_of_create = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    moderated = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.author


class Complaint(models.Model):
    reason = models.ForeignKey('ReasonOfComplaint', on_delete=models.CASCADE, verbose_name='Причина жалобы')
    text = models.TextField(verbose_name='Обоснование жалобы')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания жалобы')
    user = models.CharField(max_length=255, verbose_name='Пользователь, отправивший жалобу')
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, verbose_name='Объявление, на которое пожаловались')

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"

    def __str__(self):
        return self.reason.reason


class ReasonOfComplaint(models.Model):
    reason = models.CharField("Причина жалобы", max_length=1000)

    class Meta:
        verbose_name = 'Причина жалобы'
        verbose_name_plural = 'Причины жалобы'
        ordering = ['id']

    def __str__(self):
        return self.reason


class PhotoPublication(models.Model):
    """ Фото для публикаций """
    photo = models.ImageField(upload_to="images/publications", verbose_name="Фото")
    publication = models.ForeignKey(
        "Publication", on_delete=models.CASCADE, verbose_name="Публикация"
    )

    def __str__(self):
        return f"{self.publication}"
    

    class Meta:
        verbose_name = "Фото публикации"
        verbose_name_plural = "Фото публикаций"


@receiver(pre_delete, sender=PhotoPublication)
def photo_publications_delete(sender, instance, **kwargs):
    instance.photo.delete()


class Publication(models.Model):
    """ Модель публикаций """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    announcement = CKEditor5Field(config_name='extends', verbose_name='Аннотация')
    description = CKEditor5Field(config_name='extends', verbose_name='Текст статьи')
    preview_image = models.ImageField(upload_to="images/publications/%Y/%m/%d", verbose_name="Фото")
    video_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    date_of_create = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    counter_views = models.IntegerField(default=0, verbose_name="Счетчик просмотров")
    moderated = models.BooleanField(default=False, verbose_name="Прошло модерацию")
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
        self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
        self.search_vector = SearchVector('title', 'description', 'announcement')
        self.search_title_vector = SearchVector('title')
        super(Publication, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Publication)
def publication_photo_delete(sender, instance, **kwargs):
    """ Удаление файлов перед удалением экземпляра публикаций """
    instance.preview_image.delete(False)


class PublicationAdmin(admin.ModelAdmin):
    """ Модель публикации для Админки """
    list_display = ["id", "title", "slug"]
    list_display_links = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    ordering = [
        "date_of_create",
    ]


class Help(models.Model):
    announcement = CKEditor5Field(config_name='extends', verbose_name='Текст помощи')

    class Meta:
        verbose_name = "Текст страницы помощь"
        verbose_name_plural = "Текст страницы помощь"

    def __str__(self):
        return f'Текст страницы помощь'


class AboutOrganization(models.Model):
    '''Модель для отдает информацию об организации в footer страницы'''
    name_organization = models.CharField(max_length=255,verbose_name='Название организации')
    unp = models.CharField(max_length=9, verbose_name='УНП')
    legal_address = models.CharField(max_length=255, verbose_name='Юридический адрес')
    phone_num = models.CharField(max_length=255, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='E-Mail')
    additional_info = models.TextField(verbose_name='Дополнительная информация', null=True, blank=True)

    def __str__(self):
        return self.name_organization

    class Meta:
        verbose_name = 'Об организации'
        verbose_name_plural = 'Об организации'

