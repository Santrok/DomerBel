from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from publication.models import Publication
from services.email.message import run_send_email_task_celery
from store.models import Store


@receiver(pre_delete, sender=Publication)
def publication_photo_delete(sender, instance, **kwargs):
    """
    Удаление файла перед удалением экземпляра публикаций
    """
    instance.preview_image.delete(False)


@receiver(post_save, sender=Publication)
def notify_publication_moderation_result(sender, instance, **kwargs):
    """
    Функция проверяет, прошла ли публикацию модерацию или нет и отправляет письмо пользователю с результатом.
    """
    if instance.moderated is True:
        run_send_email_task_celery('Ваша публикация успешно прошла модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.user.email,
                                   obj="Публикация",
                                   activation_title=instance.title,
                                   result=True,
                                   moderation_error_message=instance.moderation_error_message)
    elif instance.moderated is False:
        run_send_email_task_celery('Ваша публикация не прошла модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.user.email,
                                   obj="Публикация",
                                   activation_title=instance.title,
                                   result=False,
                                   moderation_error_message=instance.moderation_error_message)
    if instance.moderation_error_message:
        sender.objects.filter(id=instance.id).update(moderation_error_message=None)
