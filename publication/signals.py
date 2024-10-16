from django.contrib.postgres.search import SearchVector
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
    if 'moderated' in instance.get_dirty_fields() and instance.moderated is True:
        run_send_email_task_celery('Ваша публикация успешно прошла модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.user.email,
                                   obj="Публикация",
                                   activation_title=instance.title,
                                   result=True,
                                   moderation_error_message=instance.moderation_error_message)
    elif 'moderated' in instance.get_dirty_fields() and instance.moderated is False:
        run_send_email_task_celery('Ваша публикация не прошла модерацию',
                                   "asend_notify_moderation_result.html",
                                   instance.user.email,
                                   obj="Публикация",
                                   activation_title=instance.title,
                                   result=False,
                                   moderation_error_message=instance.moderation_error_message)
    if instance.moderation_error_message:
        sender.objects.filter(id=instance.id).update(moderation_error_message=None)


@receiver(post_save, sender=Publication)
def create_fild_for_search_adv(sender, instance, **kwargs):
    """
    Функция заполняет поля для полнотекстового поиска.
    """
    dirty_fields = instance.get_dirty_fields()
    if (not instance.search_vector or not instance.search_title_vector or
            'title' in dirty_fields or 'description' in dirty_fields or 'announcement' in dirty_fields):
        sender.objects.filter(id=instance.id).update(search_vector=SearchVector('title',
                                                                                'description',
                                                                                'announcement'),
                                                     search_title_vector=SearchVector('title'))
