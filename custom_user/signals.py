from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserFavorites


@receiver(post_save, sender=get_user_model())
def add_user_in_permission_group(sender, instance, **kwargs):
    """
    Добавление пользователя в группу с правами доступными только юр. лицам
    """
    group = Group.objects.get_or_create(name='Юридические лица')
    try:
        if instance.entity:
            transaction.on_commit(lambda: instance.groups.add(group[0]))
        else:
            transaction.on_commit(lambda: instance.groups.remove(group[0]))
    except Exception:
        pass


@receiver(post_save, sender=get_user_model())
def create_user_favorites(sender, instance, created, **kwargs):
    """
    Создает экземпляр модели UserFavorites связанный связью OneToOne c моделью User
    """
    if created:
        UserFavorites.objects.create(user=instance)
