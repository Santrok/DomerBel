from django.contrib.postgres.search import SearchVector
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from services.email.message import run_send_email_task_celery
from store.models import Store


@receiver(pre_delete, sender=Store)
def publication_photo_delete(sender, instance, **kwargs):
    """
    Удаление файла перед удалением экземпляра магазина
    """
    instance.logo_image.delete(False)


@receiver(post_save, sender=Store)
def notify_store_moderation_result(sender, instance, **kwargs):
    """
    Функция проверяет, прошел ли магазин модерацию или нет и отправляет письмо пользователю с результатом.
    """
    if instance.moderated is True:
        run_send_email_task_celery('Ваш магазин успешно прошел модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.email,
                                   obj="Магазин",
                                   activation_title=instance.title,
                                   result=True,
                                   moderation_error_message=instance.moderation_error_message)
    elif instance.moderated is False:
        run_send_email_task_celery('Ваш магазин не прошел модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.email,
                                   obj="Магазин",
                                   activation_title=instance.title,
                                   result=False,
                                   moderation_error_message=instance.moderation_error_message)


@receiver(post_save, sender=Store)
def create_fild_for_search_adv(sender, instance, **kwargs):
    """
    Функция заполняет поля для полнотекстового поиска.
    """
    sender.objects.filter(id=instance.id).update(search_vector=SearchVector('title', 'description'))
