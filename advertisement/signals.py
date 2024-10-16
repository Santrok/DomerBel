import os

from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import Min
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from services.email.message import run_send_email_task_celery
from .models import Advertisement, PhotoAdvertisement


@receiver(pre_delete, sender=Advertisement)
def advertisement_photo_delete(sender, instance, **kwargs):
    """
    Удаление файлов и папок, перед удалением экземпляра объявления.
    """
    image_folder = os.path.dirname(instance.preview_image.path) if instance.preview_image else None
    instance.preview_image.delete(False)
    if image_folder and os.path.exists(image_folder) and os.path.isdir(image_folder):
        if not os.listdir(image_folder):
            os.rmdir(image_folder)


@receiver(pre_delete, sender=PhotoAdvertisement)
def photoadvertisement_photo_delete(sender, instance, **kwargs):
    """
    Удаление файлов перед удалением экземпляра дополнительного изображения объявления.
    """
    instance.photo.delete(False)


@receiver(post_save, sender=Advertisement)
def notify_advertisement_moderation_result(sender, instance, **kwargs):
    """
    Функция проверяет прошло ли объявление модерацию или нет и отправляет письмо пользователю с результатом.
    """
    if 'moderated' in instance.get_dirty_fields() and instance.moderated is True:
        run_send_email_task_celery('Объявление прошло модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.email,
                                   activation_title=instance.title,
                                   result=True)
    elif 'moderated' in instance.get_dirty_fields() and instance.moderated is False:
        advertisement = Advertisement.objects.get(id=instance.id)
        run_send_email_task_celery('Объявление не прошло модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.email,
                                   activation_title=instance.title,
                                   result=False,
                                   moderation_error_message=advertisement.moderation_error_message)


@receiver(post_save, sender=Advertisement)
def create_fild_for_search_adv(sender, instance, **kwargs):
    """
    Функция заполняет поля для полнотекстового поиска.
    """
    dirty_fields = instance.get_dirty_fields()
    if (not instance.search_vector or not instance.search_title_vector or
            'title' in dirty_fields or 'description' in dirty_fields):
        sender.objects.filter(id=instance.id).update(search_vector=SearchVector('title', 'description'),
                                                     search_title_vector=SearchVector('title'))


def min_count_shown_vip_advertisement(advertisements_for_sort, instance_id, fild_for_sort):
    """
    Функция устанавливает минимальное количество уже показанных vip объявлений.
    """
    min_shown_count = advertisements_for_sort.exclude(id=instance_id).aggregate(
        min_count=Min(fild_for_sort))['min_count']
    shown_count = min_shown_count if min_shown_count is not None else 0
    return shown_count


@receiver(post_save, sender=Advertisement)
def reset_all_shown_vip_and_count(sender, instance, **kwargs):
    """
    Функция устанавливает актуальное количество показанных объявлений новому VIP и
    обнуляет счетчик после отключения VIP.
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
