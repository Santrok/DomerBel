# from django.contrib.auth.models import Group
# from django.db import transaction
from django.contrib.auth.models import Group
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from users.models import User, UserFavorites, Message


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
    print(members)

    # html_content = render_to_string(
    #     "asend_message.html",
    #     context={"instance": instance, "members": members},
    # )
    #
    # for member in members:
    #     if member != instance.author:
    #         print(1)
    #         msg = EmailMultiAlternatives(
    #             "Subject here",
    #             "Тут какой-то ткст",
    #             "from@example.com",
    #             ["to@example.com"],
    #             headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
    #         )
    #         msg.attach_alternative(html_content, "text/html")
    #         msg.send()
