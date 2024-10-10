from django.db import models

# Create your models here.


class Service(models.Model):
    """Модель платной услуги"""
    service_name = models.CharField('Название услуги', max_length=300)
    cost = models.DecimalField('Стоимость услуги', max_digits=8, decimal_places=2)
    validity_period = models.PositiveIntegerField('Срок действия услуги (в днях)')
    key_word = models.CharField('Ключевое слово', max_length=50, null=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.service_name
