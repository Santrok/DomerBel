from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import UserMessage
from services.email.message import run_send_email_task_celery
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


@receiver(post_save, sender=UserMessage)
def sending_notification_about_new_message(sender, instance, **kwargs):
    members = instance.chat.members.all()
    recipient = None

    if len(members) < 2:
        chat = instance.chat
        messages = UserMessage.objects.filter(chat=chat).exclude(author=instance.author).exists()
        if messages:
            recipient = UserMessage.objects.filter(chat=chat
                                               ).exclude(author=instance.author
                                                         ).first().author
            instance.chat.members.add(recipient)
    else:
        for member in members:
            if member != instance.author:
                recipient = member

    chat_title = instance.chat.advertisement.title if instance.chat.advertisement else instance.chat.store.title

    if recipient:
        run_send_email_task_celery(chat_title,
                                   "asend_message.html",
                                   recipient.email,
                                   instance=instance,
                                   members=recipient,
                                   )
