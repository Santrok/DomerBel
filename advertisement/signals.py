import os
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_delete
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

@receiver(post_save,sender=BadWords)
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
    """ Удаление файлов перед удалением экземпляра объявления """
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
    """ Проверяем прошло ли письмо модерацию или нет и отправляем письмо пользователю """
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
def reset_all_shown_vip_count(sender, instance, **kwargs):
    """
    Функция для установки минимальное значение показанных объявлений новому VIP и
    обнуляем счетчик после отключения VIP.
    """

    # Устанавливаем минимальное значение показанных объявлений новому VIP
    if instance.vip:
        vip_ads = Advertisement.objects.filter(vip=True).order_by('shown_vip_count')
        # Если больше одного объявления, то устанавливаем количество просмотров, равное минимальному количеству просмотров
        if vip_ads.count() > 1:
            min_shown_count = vip_ads[1].shown_vip_count
            Advertisement.objects.filter(vip=True).update(shown_vip_count=min_shown_count)

    # Обнуляем счетчик после отключения VIP
    if instance.vip == False and instance.shown_vip_count > 0 or instance.shown_vip:
        Advertisement.objects.filter(id=instance.id).update(shown_vip=False, shown_vip_count=0)
