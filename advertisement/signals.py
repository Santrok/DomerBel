import os

from datetime import timedelta, datetime
from django.contrib.postgres.search import SearchVector
from django.core.cache import cache
from django.db import transaction
from django.db.models import Min
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from advertisement.models import Category, Region, Advertisement, PhotoAdvertisement, BadWords
from config.settings import env_keys
from users.tasks import send_email_task


@receiver(post_delete, sender=Category)
def object_post_delete_handler(sender, **kwargs):
    """Удаление из кэша списка категорий
    если был удален экземпляр модели Category"""
    cache.delete('objects')


@receiver(post_save, sender=Category)
def object_post_save_handler(sender, **kwargs):
    """Удаление из кэша списка категорий
        если был добавлен экземпляр модели Category"""
    cache.delete('objects')


@receiver(post_save, sender=BadWords)
def object_post_save_handler(sender, **kwargs):
    """Удаление из кэша списка нецензурных слов
        если был добавлен экземпляр модели BadWords"""
    cache.delete('objects')


@receiver(post_delete, sender=Region)
def object_post_delete_handler(sender, **kwargs):
    """Удаление из кэша списка категорий
        если был удален экземпляр модели Region"""
    cache.delete('objects')


@receiver(post_save, sender=Region)
def object_post_save_handler(sender, **kwargs):
    """Удаление из кэша списка категорий
            если был добавлен экземпляр модели Region"""
    cache.delete('objects')


@receiver(pre_delete, sender=Advertisement)
def publication_photo_delete(sender, instance, **kwargs):
    """Удаление файлов и папок, перед удалением экземпляра объявления """
    image_folder = os.path.dirname(instance.preview_image.path) if instance.preview_image else None
    instance.preview_image.delete(False)
    if image_folder and os.path.exists(image_folder) and os.path.isdir(image_folder):
        if not os.listdir(image_folder):
            os.rmdir(image_folder)


@receiver(pre_delete, sender=PhotoAdvertisement)
def publication_photo_delete(sender, instance, **kwargs):
    """ Удаление файлов перед удалением экземпляра
    дополнительного изображения объявления """
    instance.photo.delete(False)


@receiver(post_save, sender=Advertisement)
def notify_moderation_result(sender, instance, **kwargs):
    """Функция проверяет прошло ли письмо модерацию или нет и отправляем письмо пользователю с результатом"""
    # !!! Переписать на новую функцию отправки писем!!!
    if 'moderated' in instance.get_dirty_fields() and instance.moderated == True:
        html_content = render_to_string(
            "asend_notify_moderation_result.html",
            context={"activation_title": instance.title, "result": True, "url": env_keys.get("URL")},
        )

        send_email_task(chat_title='Объявление прошло модерацию',
                        recipient=instance.email,
                        text_content=html_content,
                        html_content=html_content)

    elif 'moderated' in instance.get_dirty_fields() and instance.moderated == False:
        html_content = render_to_string(
            "asend_notify_moderation_result.html",
            context={"activation_title": instance.title, "result": False, "url": env_keys.get("URL")},
        )

        send_email_task(chat_title='Объявление не прошло модерацию',
                        recipient=instance.email,
                        text_content=html_content,
                        html_content=html_content)


@receiver(post_save, sender=Advertisement)
def create_date_of_deactivate_and_delete(sender, instance, **kwargs):
    """Функция заполняет поля для полнотекстового поиска"""
    dirty_fields = instance.get_dirty_fields()
    if (not instance.search_vector or not instance.search_title_vector or
            'title' in dirty_fields or 'description' in dirty_fields):
        sender.objects.filter(id=instance.id).update(search_vector=SearchVector('title', 'description'),
                                                     search_title_vector=SearchVector('title'))


def min_count_shown_vip_advertisement(advertisements_for_sort, instance_id, fild_for_sort):
    min_shown_count = advertisements_for_sort.exclude(id=instance_id).aggregate(
        min_count=Min(fild_for_sort))['min_count']
    shown_count = min_shown_count if min_shown_count is not None else 0
    return shown_count


@receiver(post_save, sender=Advertisement)
def reset_all_shown_vip_and_count(sender, instance, **kwargs):
    """
    Функция устанавливает актуальное количество показанных объявлений новому VIP и
    обнуляем счетчик после отключения VIP.
    """
    if 'vip' not in instance.get_dirty_fields():
        return

    with transaction.atomic():
        advertisement = Advertisement.objects.filter(id=instance.id)

        # Обнуляем счетчик после отключения VIP
        if not instance.vip:
            advertisement.update(shown_vip=False,
                                 shown_vip_count=0,
                                 shown_vip_category=False,
                                 shown_vip_category_count=0)
            return

        # Находим объявления по всем категориям и по конкретной категории
        vip_ads = Advertisement.objects.filter(moderated=True, is_active=True, vip=True)
        vip_ads_category = Advertisement.objects.filter(moderated=True,
                                                        is_active=True,
                                                        vip=True,
                                                        category=instance.category)

        # Устанавливаем минимальное значение показов по всем объявлениям
        shown_count = min_count_shown_vip_advertisement(vip_ads,
                                                        instance.id,
                                                        'shown_vip_count')

        # Устанавливаем минимальное значение показов в категории
        shown_category_count = min_count_shown_vip_advertisement(vip_ads_category,
                                                                 instance.id,
                                                                 'shown_vip_category_count')

        advertisement.update(shown_vip_count=shown_count,
                             shown_vip_category_count=shown_category_count, )
