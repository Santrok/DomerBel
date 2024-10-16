from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category, Region


@receiver(post_delete, sender=Category)
def object_post_delete_handler(sender, **kwargs):
    """
    Удаление из кэша списка категорий если был удален экземпляр модели Category
    """
    cache.delete('objects')


@receiver(post_save, sender=Category)
def object_post_save_handler(sender, **kwargs):
    """
    Удаление из кэша списка категорий если был добавлен экземпляр модели Category
    """
    cache.delete('objects')


@receiver(post_delete, sender=Region)
def object_post_delete_handler(sender, **kwargs):
    """
    Удаление из кэша списка категорий если был удален экземпляр модели Region
    """
    cache.delete('objects')


@receiver(post_save, sender=Region)
def object_post_save_handler(sender, **kwargs):
    """
    Удаление из кэша списка категорий если был добавлен экземпляр модели Region
    """
    cache.delete('objects')
