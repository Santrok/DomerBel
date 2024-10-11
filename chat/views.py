from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render, get_object_or_404, redirect

from chat.models import Chat, UserMessage


@login_required
def get_all_user_dialogs(request):
    """
    Сборка страницы которая отображает все диалоги пользователя в ЛК.
    Модели: Chat, UserMessage
    """
    chats = Chat.objects.filter(members__in=[request.user.id]
                                ).annotate(last_message=Max('usermessage__pub_date')
                                           ).order_by("-last_message"
                                                      ).prefetch_related('usermessage_set', 'usermessage_set__chat'
                                                                         ).select_related('advertisement__category',
                                                                                          'advertisement', 'store',
                                                                                          'store__category')
    unread_chat = UserMessage.objects.filter(chat__in=chats, is_read=False).exclude(author=request.user).exists()
    context = {
        "chats": chats,
        "unread_chat": unread_chat,
        "adaptive_navigation": "Мои сообщения"
    }
    return render(request, 'profile_dialogs.html', context)


@login_required
def view_message_in_dialog(request, chat_id, chat_name):
    """
    Сборка страницы которая отображает все сообщения внутри выбранного диалога.
    Модели: Chat, UserMessage
    """
    chat = get_object_or_404(Chat, id=chat_id, members=request.user)
    UserMessage.objects.filter(chat=chat, is_read=False).exclude(author=request.user).update(is_read=True)
    context = {
        "chat": chat,
    }
    return render(request, 'profile_dialog.html', context)


@login_required
def delete_user_dialog(request):
    """
    Удаляет выбранный диалог в ЛК
    Модели: Chat, UserMessage
    """
    if request.method == "POST":
        if 'dialog' in request.POST:
            dialog = get_object_or_404(Chat, id=request.POST.get('dialog'), members=request.user)
            dialog.members.remove(request.user)
            messages.success(request, "Диалог удален!")
        return redirect('dialogs')

