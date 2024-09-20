from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from config.settings import env_keys
from users.models import User, UserFavorites, Message
from users.tasks import send_email_task


@receiver(post_save, sender=User)
def add_user_in_permission_group(sender: User, instance: User, **kwargs):
    """Добавление пользователя в группу
    с правами доступными только юр. лицам"""
    group = Group.objects.get(name='Юридические лица')
    try:
        if instance.entity:
            transaction.on_commit(lambda: instance.groups.add(group))
        else:
            transaction.on_commit(lambda: instance.groups.remove(group))
    except Exception:
        pass


@receiver(post_save, sender=User)
def create_user_favorites(sender, instance, created, **kwargs):
    if created:
        UserFavorites.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_favorites(sender, instance, **kwargs):
    instance.userfavorites.save()


@receiver(post_save, sender=Message)
def save_user_favorites(sender, instance, **kwargs):
    members = instance.chat.members.all()

    recipient = None
    for member in members:
        if member != instance.author:
            recipient = member

    html_content = render_to_string(
        "asend_message.html",
        context={"instance": instance, "members": recipient, "url": env_keys.get("URL")},
    )
    text_content = render_to_string(
        "asend_message.html",
        context={"instance": instance, "members": recipient, "url": env_keys.get("URL")},
    )

    chat_title = instance.chat.advertisement.title if instance.chat.advertisement else instance.chat.store.title
    send_email_task.delay(chat_title=chat_title, recipient=recipient.email, text_content=text_content, html_content=html_content)

