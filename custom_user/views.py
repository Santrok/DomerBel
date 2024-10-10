from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EditContactDataForm, ChangePasswordForm


@login_required
def get_user_data_page_and_change_user_data(request):
    """Сборка страницы для отображения данных в личном кабинете пользователя
        и обрабатывает две формы на изменение контактных данных
         и изменение пароля пользователя.
          Модели: User.
           Формы: ChangePasswordForm, EditContactDataForm"""
    user = request.user
    edit_contact_data_form = EditContactDataForm(instance=user)
    change_password_form = ChangePasswordForm()
    if request.method == "POST":

        if 'edit_contact_data' in request.POST:
            edit_contact_data_form = EditContactDataForm(request.POST, instance=user)
            if edit_contact_data_form.is_valid():
                edit_contact_data_form.save()
                messages.success(request, "Ваши контактные данные успешно изменены!")
                return redirect('user_data')

        elif 'change_password' in request.POST:
            change_password_form = ChangePasswordForm(request.POST, instance=user)
            if change_password_form.is_valid():
                current_password = change_password_form.cleaned_data.get("password")
                new_password = change_password_form.cleaned_data.get("new_password")
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Ваш пароль успешно изменён!")
                    return redirect('user_data')
                else:
                    messages.error(request, "Неверный текущий пароль.")

    context = {'edit_contact_data_form': edit_contact_data_form,
               'change_pass_form': change_password_form,
               "adaptive_navigation": "Контактные данные"
               }

    return render(request, 'profile_data.html', context)
