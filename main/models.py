from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
# Create your models here.


class AboutOrganization(models.Model):
    """Модель для хранения установочных данных об организации ДОМЕР.бел"""
    name_organization = models.CharField('Название организации', max_length=255)
    unp = models.CharField('УНП', max_length=9)
    legal_address = models.CharField('Юридический адрес', max_length=255)
    phone_num = models.CharField('Номер телефона', max_length=255)
    email = models.EmailField('E-Mail')
    additional_info = models.TextField('Дополнительная информация', null=True, blank=True)

    class Meta:
        verbose_name = 'Об организации'
        verbose_name_plural = 'Об организации'

    def __str__(self):
        return self.name_organization


class Help(models.Model):
    """Модель для хранения информации о правилах пользования ресурсом"""
    announcement = CKEditor5Field('Текст помощи', config_name='extends')

    class Meta:
        verbose_name = "Текст страницы помощь"
        verbose_name_plural = "Текст страницы помощь"

    def __str__(self):
        return f'Текст страницы помощь'


class BadWords(models.Model):
    """Модель для хранения слов для валидатора нецензурных слов"""
    word = models.CharField("Слово", max_length=255)

    class Meta:
        verbose_name = 'Нецензурное слово'
        verbose_name_plural = 'Нецензурные слова'

    def __str__(self):
        return self.word[0:2] + '*' * (len(self.word) - 3) + self.word[-1]
