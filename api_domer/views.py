import smtplib
from zipfile import ZipFile
import openpyxl
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.expressions import result
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.decorators import api_view
from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from advertisement.models import (Region, Category, Field, ElementTwo, PhotoAdvertisement, Advertisement, Store,
                                  Element, UploadFile, ErrorFile)
from api_domer.serializers import (GetListOfCitiesSerializer, GetListOfCategoriesSerializer, FieldSerialier,
                                   ElementTwoSerializer, AdvertisementSerializer, StoreSerializer,
                                   UserRegisterSerializer, UserLoginSerializer, PasswordResetSerializer,
                                   FavoriteSerializer, ElementSerializer, GetListOfCategoriesFieldsSerializer,
                                   ReasonOfComplaintSerializer, ComplaintSerializer, MessageSerializer,
                                   UploadFileSerializer, StatusUnreadUserMessage)
from api_domer.tasks import save_advertisement_task, update_advertisement_task

from api_domer.utils import validate_additional_information, save_temp_photos
from config import settings
from config.settings import env_keys
from main_page_domer.models import ReasonOfComplaint
from users.models import User, UserFavorites, Chat, Message
from advertisement.tasks import save_many_ads_from_zip_task, save_many_ads_from_excel_task
from config.celery_app import app
from users.tasks import send_email_task


# Отдаёт список городов type='Город' по id выбранной области type='Область' из модели Region
@api_view(["GET", "POST"])
def get_list_of_cities(request, id):
    cities = Region.objects.filter(parent_id=id)
    serializer = GetListOfCitiesSerializer(cities, many=True)
    return Response(serializer.data)


# Отдаёт список всех категорий из модели Category для добавления/редактирования магазина
@api_view(["GET", "POST"])
def get_list_of_categories(request):
    categories = Category.objects.filter(level__lte=1)
    serializer = GetListOfCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


# Отдает список дочерних категорий по родительскому id (для поиска магазинов и поиска в ЛК)
@api_view(["GET", "POST"])
def get_categories_for_search(request, id):
    categories = Category.objects.filter(parent_id=id)
    serializer = GetListOfCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_region_list(request):
    regions = Region.objects.all()
    serializer = GetListOfCitiesSerializer(regions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_list(request):
    categories = Category.objects.filter(parent_id=request.query_params.get('id'))
    serializer = GetListOfCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_field_list(request):
    fieldlist = Field.objects.filter(category_id=request.query_params.get('id')).select_related(
        'spisok').prefetch_related('spisok__element_set__elementtwo_set').order_by('id')
    serializer = FieldSerialier(fieldlist, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_elementtwo_list(request):
    if request.query_params.get('slug') == 'undefined':
        return Response()
    else:
        elementstwo = ElementTwo.objects.filter(element_id=request.query_params.get('slug'))
        serializer = ElementTwoSerializer(elementstwo, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_store_for_advertisement(request):
    stores = Store.objects.filter(user=request.user.id)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def save_advertisement(request):
    additional_information = dict(request.data.copy())
    serializer = AdvertisementSerializer(data=request.data, context={"request": request})
    serializer.is_valid()
    keys_to_delete = ['csrfmiddlewaretoken', 'preview_img']
    keys_to_delete.extend(serializer.data.keys())
    serializer_additional_error, additional_information = validate_additional_information(keys_to_delete,
                                                                                          additional_information)
    if not serializer.errors and not serializer_additional_error.data:
        data = dict(serializer.validated_data)
        data['category_id'] = data.pop('category').id
        data['region_id'] = data.pop('region').id
        data['store_id'] = data.pop('store').id if data.get('store') else None
        photo_list = data.pop('photo', None)

        # Временно сохраняем фотографии что-бы переделать их адреса в celery
        temporarily_saving_photos = save_temp_photos(photo_list, request.data.get("preview_img")) if photo_list else None

        # Вызываем задачу celery для сохранения объявлений
        save_advertisement_task.delay(request.user.id, data, additional_information, temporarily_saving_photos)

        return Response({
            "success": "<p>Ваше объявление отправлено на модерацию.</p><p>После модерации оно появится в списке объявлений.</p>",
            "link": f"{env_keys.get('URL')}", "link_text": "Вернуться на главную"},
            status=status.HTTP_201_CREATED)
    else:
        raise serializers.ValidationError(
            {"error_additional": serializer_additional_error.data, "error": serializer.errors})


@api_view(['PATCH'])
def update_advertisement(request):
    # Проверяем есть ли такое объявление у пользователя если нет выдаем ошибку
    try:
        advertisement = Advertisement.objects.get(id=request.data.get('advertisement'), author=request.user.id)
    except Advertisement.DoesNotExist:
        raise serializers.ValidationError(
            {"error": {'advertisement_error': {"text": "<p>Ошибка сохранения объявления, попробуйте еще раз</p>",
                                               "link": f"{env_keys.get('URL')}/users/personal_account/",
                                               "link_text": "В мой кабинет"}}})

    additional_information = dict(request.data.copy())
    serializer = AdvertisementSerializer(data=request.data)
    serializer.is_valid()
    keys_to_delete = ['csrfmiddlewaretoken', 'preview_img', 'deleted_images', 'advertisement']
    keys_to_delete.extend(serializer.data.keys())
    serializer_additional_error, additional_information = validate_additional_information(keys_to_delete,
                                                                                          additional_information)

    if not serializer.errors and not serializer_additional_error.data:
        data = dict(serializer.validated_data)
        data['category_id'] = data.pop('category').id
        data['region_id'] = data.pop('region').id
        data['store_id'] = data.pop('store').id if data.get('store') else None
        new_photo_list = data.pop('photo', [])
        preview_photo = request.data.get('preview_img')
        deleted_photo = request.data.get('deleted_images').split(',') if request.data.get('deleted_images') else None

        # Проверка, изменилось ли главное изображение
        if advertisement.preview_image != preview_photo and preview_photo not in [i.name for i in new_photo_list]:
            new_preview_photo_from_old_ones = preview_photo
        else:
            new_preview_photo_from_old_ones = None

        # Временно сохраняем новые фотографии что-бы переделать их адреса в celery
        temporarily_saving_photos = save_temp_photos(new_photo_list,
                                          request.data.get("preview_img")) if new_photo_list != [] else None

        # Вызываем задачу celery для сохранения объявлений
        update_advertisement_task.delay(request.user.id, request.data.get('advertisement'), data,
                                        additional_information, temporarily_saving_photos, new_preview_photo_from_old_ones,
                                        deleted_photo)

        return Response({
            "success": "<p>Ваше объявление отправлено на модерацию.</p><p>После модерации оно появится в списке объявлений.</p>",
            "link": f"{env_keys.get('URL')}/users/personal_account/", "link_text": "В мой кабинет"},
            status=status.HTTP_201_CREATED)

    else:
        raise serializers.ValidationError(
            {"error_additional": serializer_additional_error.data, "error": serializer.errors})


@api_view(["POST"])
def registration_user(request):
    registration_serializer = UserRegisterSerializer(data=request.data, context={"request": request})
    if registration_serializer.is_valid():
        registration_serializer.save()
        return Response({'success': 'Вы успешно зарегистрированы'}, status=status.HTTP_201_CREATED)
    else:
        raise serializers.ValidationError(
            {"errors": registration_serializer.errors})


@api_view(["POST"])
def login_user(request):
    login_serializer = UserLoginSerializer(data=request.data, context={"request": request})
    if login_serializer.is_valid():
        user = authenticate(**login_serializer.validated_data)
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            raise serializers.ValidationError({"errors": {
                "email": "Пользователь не найден. Проверьте правильность введенных данных.", "password": ''}})
    else:
        raise serializers.ValidationError({"errors": login_serializer.errors})


@api_view(["POST"])
def logout_user(request):
    try:
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def password_reset(request):
    password_reset_serializer = PasswordResetSerializer(data=request.data, context={"request": request})
    if password_reset_serializer.is_valid():
        email = password_reset_serializer.validated_data.get('email')
        url = env_keys.get("URL")
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = reverse_lazy('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        html_content = render_to_string(
            "asend_reset_password.html",
            context={"activation_url": activation_url, "url": url},
        )
        text_content = render_to_string(
            "asend_reset_password.html",
            context={"activation_url": activation_url, "url": url},
        )

        send_email_task.delay(chat_title='Восстановление пароля на сайте Домер.бел',
                                                   recipient=email,
                                                   text_content=text_content, html_content=html_content)
        return Response({'success': 'На ваш адрес электронной почты было отправлено письмо для восстановления '
                                    'пароля. Если письмо не пришло, проверьте папку спам.'},
                        status=status.HTTP_200_OK)

    else:
        raise serializers.ValidationError(
            {"errors": password_reset_serializer.errors})


@api_view(['POST'])
def add_to_favorite(request):
    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_favorites = get_object_or_404(UserFavorites, user=request.user)
        if not serializer.validated_data.get('id') in user_favorites.favorites:
            user_favorites.favorites.append(serializer.validated_data.get('id'))
            user_favorites.save()
        return Response({'success': 'Объявление успешно добавлено в избранное'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def delete_from_favorite(request):
    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_favorites = get_object_or_404(UserFavorites, user=request.user)
        if serializer.validated_data.get('id') in user_favorites.favorites:
            user_favorites.favorites.remove(serializer.validated_data.get('id'))
            user_favorites.save()
        return Response({'success': 'Объявление успешно удалено из избранного'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_element_list(request):
    """Отадет элементы связанные с полем по id"""
    elements = Element.objects.filter(spisok_id__field=request.query_params.get('id'))
    serializer = ElementSerializer(elements, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_subcategory_list(request):
    """Отдает подкатегориии и их поля по id категории"""
    categories = Category.objects.filter(parent_id=request.query_params.get('id')).prefetch_related(
        'field_set__spisok__element_set__elementtwo_set')
    serializer = GetListOfCategoriesFieldsSerializer(categories, many=True)
    return Response(serializer.data)


class ReasonOfComplaintView(ListAPIView):
    queryset = ReasonOfComplaint
    serializer_class = ReasonOfComplaintSerializer


@api_view(['POST'])
def save_complaint(request):
    serializer = ComplaintSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        reason = serializer.validated_data.get("reason")
        text = serializer.validated_data.get('text')
        user = serializer.validated_data.get("user")
        advertisement = serializer.validated_data.get("advertisement")

        subject = f'Жалоба от пользователя {user} на объявление  id={advertisement.id}.'
        message = text

        html_content = render_to_string(
            "asend_complaint.html",
            context={"message": message, "subject": subject, "reason": reason, "url": env_keys.get("URL")},
        )
        text_content = render_to_string(
            "asend_complaint.html",
            context={"message": message, "subject": subject, "reason": reason, "url": env_keys.get("URL")},
        )

        send_email_task.delay(chat_title="Жалоба",
                              recipient=settings.EMAIL_HOST_USER,
                              text_content=text_content,
                              html_content=html_content)

        return Response({'success': 'Ваша жалоба на объявление отправлена администрации сайта'},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors})


def get_chat_object(chat_object, model, author_field, user):
    try:
        obj = model.objects.get(id=chat_object)
        if getattr(obj, author_field) == user:
            return None, Response({'error': 'Вы не можете написать самому себе'}, status=status.HTTP_400_BAD_REQUEST)
        return obj, None
    except model.DoesNotExist:
        return None, Response({'error': 'Ошибка: объект чата не найден'}, status=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    # logger.error(f"Ошибка при получении объявления: {str(e)}")


@api_view(['POST'])
def create_chat(request):
    serializer = MessageSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    chat_object = {}
    chat_type = None

    if request.data.get('advertisement'):
        chat_type = 'advertisement'
        advertisement, error_response = get_chat_object(serializer.validated_data.get('chat_object'), Advertisement,
                                                        'author_id', request.user.id)
        if error_response:
            return error_response
        chat_object['advertisement'] = advertisement

    elif request.data.get('store'):
        chat_type = 'store'
        store, error_response = get_chat_object(serializer.validated_data.get('chat_object'), Store,
                                                'user_id', request.user.id)
        if error_response:
            return error_response
        chat_object['store'] = store

    if not chat_type:
        return Response({'error': 'Ошибка: объект чата не найден'}, status=status.HTTP_400_BAD_REQUEST)

    chat_object['members'] = (advertisement.author_id if chat_type == 'advertisement' else store.user_id)

    chat_exists = Chat.objects.filter(members=request.user).filter(**chat_object).exists()

    if chat_object.get('members'):
        with transaction.atomic():
            if not chat_exists:
                chat = Chat.objects.create(**chat_object)
                chat.members.set([request.user.id, chat_object['members']])
            else:
                chat = Chat.objects.filter(**chat_object, members=request.user).first()

            Message.objects.create(chat=chat, author=request.user,
                                   message=serializer.validated_data.get('text_message'))

            return Response({'success': 'Ваше сообщение отправлено'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Ошибка: вероятно автор объявления не зарегистрирован'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_bulk_import_of_ads(request):
    serializer = UploadFileSerializer(data=request.data)
    if serializer.is_valid():
        if serializer.validated_data.get("file").name.endswith('xlsx'):
            '''Работа с электронной таблицей'''
            try:
                uploud_file = serializer.validated_data.get("file")
                book = openpyxl.open(uploud_file, read_only=True)
                save_file = UploadFile(file=uploud_file, user=request.user)
                save_file.save()
                ads = save_many_ads_from_excel_task.delay(uploud_file=f'./media/{save_file.file.name}',
                                                          id=request.user.id,
                                                          first_name=request.user.first_name,
                                                          phone_number=request.user.phone_number,
                                                          email=request.user.email)
                return Response({'task_id': f'{ads.task_id}'})
            except:
                return Response({'error': 'Невозможно прочитать файл.'})

        elif serializer.validated_data.get("file").name.endswith('zip'):
            '''Работа с электронным архивом'''
            try:
                uploud_zip = serializer.validated_data.get("file")
                with ZipFile(uploud_zip, 'r') as zip:
                    files_from_zip = zip.namelist()
                save_zip = UploadFile(file=uploud_zip, user=request.user)
                save_zip.save()
                ads = save_many_ads_from_zip_task.delay(uploud_zip=f'./media/{save_zip.file.name}',
                                                        id=request.user.id,
                                                        first_name=request.user.first_name,
                                                        phone_number=request.user.phone_number,
                                                        email=request.user.email)
                return Response({'task_id': f'{ads.task_id}'})
            except:
                return Response({'error': 'Невозможно прочитать файл.'})
    else:
        return Response({'error': 'Ошибка при загрузке файла. Убедитесь, что загружаемый файл необходимого расширения'})



@api_view(["GET", "POST"])
def get_result_task(request,id):
    '''Отдает прогресс выполнения таски и результат'''
    task = app.AsyncResult(id=id)
    if task.state == "SUCCESS":
        return JsonResponse({'state': task.state, 'result':task.result})
    else:
        return JsonResponse({'state': task.state})


@api_view(['GET'])
def status_unread_message_user(request):
    chats = Chat.objects.filter(members__in=[request.user.id])
    unread_chat = Message.objects.filter(chat__in=chats, is_read=False).exclude(author=request.user).exists()
    return Response({"status": unread_chat})
