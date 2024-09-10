from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from main_page_domer.models import AboutOrganization, Publication


@receiver(pre_delete, sender=Publication)
def publication_photo_delete(sender, instance, **kwargs):
    """ Удаление файлов перед удалением экземпляра публикаций """
    instance.preview_image.delete(False)


@receiver(post_delete, sender=(AboutOrganization))
def object_post_delete_handler(sender, **kwargs):
    """Удаление из кэша информации об организации
    если был удален экземпляр модели AboutOrganization"""
    cache.delete('about_organization')


@receiver(post_save, sender=AboutOrganization)
def object_post_save_handler(sender, **kwargs):
    """Удаление из кэша информации об организации
        если был добавлен экземпляр модели AboutOrganization"""
    cache.delete('about_organization')