from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from advertisement.models import Category, Region, Advertisement, PhotoAdvertisement, BadWords


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
    instance.preview_image.delete(False)


@receiver(pre_delete, sender=PhotoAdvertisement)
def publication_photo_delete(sender, instance, **kwargs):
    """ Удаление файлов перед удалением экземпляра
    дополнительного изображения объявления """
    instance.photo.delete(False)


@receiver(post_save, sender=Advertisement)
def ffff(sender, instance, **kwargs):
    if 'moderated' in instance.get_dirty_fields() and instance.moderated == True:
        print('письмо ушло в пользователю прошло модерацию')
    elif 'moderated' in instance.get_dirty_fields() and instance.moderated == False:
        print('письмо ушло в пользователю не прошло модерацию')
