from django.db.models.signals import pre_delete
from django.dispatch import receiver

from publication.models import Publication


@receiver(pre_delete, sender=Publication)
def publication_photo_delete(sender, instance, **kwargs):
    """ Удаление файла перед удалением экземпляра публикаций """
    instance.preview_image.delete(False)
