import uuid

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from advertisement.models import Advertisement
from store.models import Store


# Create your models here.
class Chat(models.Model):
    """
    Модель чата для диалогов между пользователями.
    Модели: User(M2M), Advertisement(FK), Store(FK)
    """
    chat_name = models.UUIDField("Идентификатор чата", default=uuid.uuid4, unique=True, editable=False)
    members = models.ManyToManyField(get_user_model(), verbose_name='Участник')
    advertisement = models.ForeignKey(Advertisement, verbose_name="Объявление", on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, verbose_name="Магазин", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'{self.chat_name}'

    def get_absolute_url(self):
        return reverse('messages', kwargs={'chat_name': self.chat_name, 'chat_id': self.pk})


class ChatAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: Chat
    """
    pass


class UserMessage(models.Model):
    """
    Модель сообщения пользователя в диалоге.
    Модели: User(M2M), Chat(FK)
    """
    chat = models.ForeignKey(Chat, verbose_name='Чат', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.CASCADE)
    message = models.TextField('Сообщение')
    pub_date = models.DateTimeField('Дата сообщения', auto_now_add=True)
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['pub_date']

    def __str__(self):
        return f'Чат_id: {self.chat.id}, автор: {self.author.first_name}.'


class UserMessageAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: UserMessage
    """
    pass
