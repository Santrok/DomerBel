from datetime import datetime, timedelta
from zipfile import ZipFile

import openpyxl
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from advertisement.models import Advertisement, UploadFile
from chat.models import Chat, UserMessage
from config import settings
from config.celery_app import app
from config.settings import env_keys
from custom_user.models import UserFavorites
from custom_user.services import make_activation_url_for_reset_password
from paid_service.models import Service
from paid_service.services import send_payment_request
from related_data.models import Region, Category, Field, ElementTwo, Element
from services.email.message import run_send_email_task_celery
from store.models import Store
from .serializers import (AdvertisementSerializer, ComplaintSerializer, UserMessageSerializer, UserRegisterSerializer,
                          UserLoginSerializer, PasswordResetSerializer, FavoriteSerializer, PaidSerializer,
                          RegionSerializer, CategorySerializer, CategoryFieldsSerializer, FieldSerialier,
                          ElementTwoSerializer, StoreSerializer, ElementSerializer, UploadFileSerializer)
from .utils import validate_additional_information, save_temp_photos, get_chat_object
from advertisement.tasks import save_advertisement_task, update_advertisement_task, save_many_ads_from_excel_task, \
    save_many_ads_from_zip_task


@api_view(['POST'])
def save_advertisement(request):
    """
    Принимает данные для создания нового объявления,
    проверяет их и запускает задачу на Celery для сохранения объявления.
    Сериализаторы: AdvertisementSerializer
    """
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

        # Временное сохранение новых фотографий что-бы переделать их адреса в celery
        temporarily_saving_photos = save_temp_photos(photo_list,
                                                     request.data.get("preview_img")) if photo_list else None

        # Вызов задачи celery для сохранения объявлений
        save_advertisement_task.delay(request.user.id, data, additional_information, temporarily_saving_photos)

        return Response({
            "success": """<p>Ваше объявление отправлено на модерацию.</p>
                       <p>После модерации оно появится в списке объявлений.</p>""",
            "link": f"{env_keys.get('URL')}", "link_text": "Вернуться на главную"},
            status=status.HTTP_201_CREATED)
    else:
        raise serializers.ValidationError(
            {"error_additional": serializer_additional_error.data, "error": serializer.errors})


@api_view(['PATCH'])
def update_advertisement(request):
    """
    Принимает данные для изменения объявления пользователя,
    проверяет их и запускает задачу на Celery для изменения объявления.
    Модели: Advertisement.
    Сериализаторы: AdvertisementSerializer
    """
    try:
        advertisement = Advertisement.objects.get(id=request.data.get('advertisement'), author=request.user.id)
    except Advertisement.DoesNotExist:
        raise serializers.ValidationError(
            {"error": {'advertisement_error': {"text": "<p>Ошибка сохранения объявления, попробуйте еще раз</p>",
                                               "link": f"{env_keys.get('URL')}/personal_account/",
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

        # Временное сохранение новых фотографий что-бы переделать их адреса в celery
        temporarily_saving_photos = save_temp_photos(new_photo_list,
                                                     request.data.get("preview_img")) if new_photo_list != [] else None

        # Вызов задачи celery для сохранения объявлений
        update_advertisement_task.delay(request.user.id, request.data.get('advertisement'), data,
                                        additional_information, temporarily_saving_photos,
                                        new_preview_photo_from_old_ones,
                                        deleted_photo)

        return Response({
            "success": "<p>Ваше объявление отправлено на модерацию.</p>"
                       "<p>После модерации оно появится в списке объявлений.</p>",
            "link": f"{env_keys.get('URL')}/personal_account/archived_adds/", "link_text": "В мой кабинет"},
            status=status.HTTP_201_CREATED)

    else:
        raise serializers.ValidationError(
            {"error_additional": serializer_additional_error.data, "error": serializer.errors})


@api_view(['POST'])
def save_complaint_and_send_complaint_to_administration_email(request):
    """
    Создает экземпляр модели Complaint
    и отправляет жалобу администрации сайта.
    Сериализаторы: ComplaintSerializer
    """
    serializer = ComplaintSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        reason = serializer.validated_data.get("reason")
        text = serializer.validated_data.get('text')
        user = serializer.validated_data.get("user")
        advertisement = serializer.validated_data.get("advertisement")

        subject = f'Жалоба от пользователя {user} на объявление  id={advertisement.id}.'
        message = text

        run_send_email_task_celery("Жалоба",
                                   "asend_complaint.html",
                                   settings.EMAIL_HOST_USER,
                                   message=message,
                                   subject=subject,
                                   reason=reason,
                                   ads_url=advertisement.get_absolute_url())

        return Response({'success': 'Ваша жалоба на объявление отправлена администрации сайта'},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors})


@api_view(['POST'])
def create_new_chat_and_create_new_message(request):
    """
    Определяет объект чата, проверяет существование чата,
    если его нет - создает новый чат, создает новое сообщение в чате.
    Модели: Chat, UserMessage.
    Сериализаторы: UserMessageSerializer.
    """
    serializer = UserMessageSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    chat_object = {}
    chat_type = None

    if request.data.get('advertisement'):
        chat_type = 'advertisement'
        advertisement, error_response = get_chat_object(serializer.validated_data.get('chat_object'),
                                                        Advertisement,
                                                        'author_id',
                                                        request.user.id)
        if error_response:
            return error_response
        chat_object['advertisement'] = advertisement
    elif request.data.get('store'):
        chat_type = 'store'
        store, error_response = get_chat_object(serializer.validated_data.get('chat_object'),
                                                Store,
                                                'user_id',
                                                request.user.id)
        if error_response:
            return error_response
        chat_object['store'] = store

    if not chat_type:
        return Response({'error': 'Объект чата не найден'}, status=status.HTTP_400_BAD_REQUEST)

    chat_object['members'] = (advertisement.author_id if chat_type == 'advertisement' else store.user_id)

    if chat_object.get('members'):
        chat_exists = Chat.objects.filter(members=request.user).filter(**chat_object).exists()
        with transaction.atomic():
            if not chat_exists:
                member = chat_object.pop('members')
                chat = Chat.objects.create(**chat_object)
                chat.members.set([request.user.id, member])
            else:
                chat = Chat.objects.filter(members=request.user).filter(**chat_object).first()

            UserMessage.objects.create(chat=chat, author=request.user,
                                       message=serializer.validated_data.get('text_message'))

            return Response({'success': 'Ваше сообщение отправлено'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Ошибка: возможно автор объявления не зарегистрирован'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def status_unread_message_user(request):
    """
    Возвращает информацию о том, есть ли у пользователя непрочитанные сообщения.
    Модели: Chat, UserMessage
    """
    chats = Chat.objects.filter(members__in=[request.user.id])
    unread_chat = UserMessage.objects.filter(chat__in=chats, is_read=False).exclude(author=request.user).exists()
    return Response({"status": unread_chat})


@api_view(["POST"])
def registration_user(request):
    """
    Функция для регистрации нового пользователя.
    Сериализаторы: UserRegisterSerializer
    """
    registration_serializer = UserRegisterSerializer(data=request.data, context={"request": request})

    if registration_serializer.is_valid():
        try:
            registration_serializer.save()
            if registration_serializer.validated_data.get('entity'):
                run_send_email_task_celery('Зарегистрировано юридическое лицо на сайте ДОМЕР.бел',
                                           'asend_notification_new_user.html',
                                           settings.EMAIL_HOST_USER,
                                           first_name=registration_serializer.validated_data.get('first_name'),
                                           email=registration_serializer.validated_data.get('email'),
                                           phone=registration_serializer.validated_data.get('phone_number'),
                                           )
                return Response({'success': 'Вы успешно зарегистрированы. '
                                            'В ближайшее время с вами свяжутся для заключения договора'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'success': 'Вы успешно зарегистрированы'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError({"error": """Произошла ошибка при регистрации.
                                                            Пожалуйста, попробуйте позже"""
                                               })

    raise serializers.ValidationError({"errors": registration_serializer.errors})


@api_view(["POST"])
def login_user(request):
    """
    Функция для аутентификации и авторизации пользователя.
    Сериализаторы: UserLoginSerializer
    """
    login_serializer = UserLoginSerializer(data=request.data, context={"request": request})

    if not login_serializer.is_valid():
        raise serializers.ValidationError({"errors": login_serializer.errors})

    user = authenticate(**login_serializer.validated_data)

    if user is not None:
        login(request, user)
        return Response(status=status.HTTP_205_RESET_CONTENT)

    raise serializers.ValidationError({"errors": {
        "email": "Пользователь не найден. Проверьте правильность введенных данных.", "password": ''}})


@api_view(["POST"])
def logout_user(request):
    """
    Функция для выхода пользователя из системы.
    """
    try:
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def password_reset(request):
    """
    Функция для сброса пароля пользователя через Email.
    Модели: User.
    Сериализаторы: PasswordResetSerializer
    """
    password_reset_serializer = PasswordResetSerializer(data=request.data, context={"request": request})

    if password_reset_serializer.is_valid():
        email = password_reset_serializer.validated_data.get('email')
        user = get_user_model()

        try:
            user = user.objects.get(email=email)
        except user.DoesNotExist:
            # Не сообщаем пользователю, существует ли такой email
            return Response({
                'success': 'На ваш адрес электронной почты было отправлено письмо для восстановления '
                           'пароля. Если письмо не пришло, проверьте папку спам.'
            }, status=status.HTTP_200_OK)
        else:
            activation_url = make_activation_url_for_reset_password(user)

            run_send_email_task_celery('Восстановление пароля на сайте Домер.бел',
                                       'asend_reset_password.html',
                                       email,
                                       activation_url=activation_url
                                       )

            return Response({
                'success': 'На ваш адрес электронной почты было отправлено письмо для восстановления '
                           'пароля. Если письмо не пришло, проверьте папку спам.'
            }, status=status.HTTP_200_OK)

    raise serializers.ValidationError({"errors": password_reset_serializer.errors})


@api_view(['POST'])
def add_to_favorite(request):
    """
    Функция для добавления id объявления в избранное пользователя.
    Модели: UserFavorites.
    Сериализаторы: FavoriteSerializer
    """
    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_favorites = get_object_or_404(UserFavorites, user=request.user)
        if not serializer.validated_data.get('id') in user_favorites.favorites:
            user_favorites.favorites.append(serializer.validated_data.get('id'))
            user_favorites.save()
        return Response({'success': 'Объявление успешно добавлено в избранное'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def delete_from_favorite(request):
    """
    Функция для удаления id объявления в избранное пользователя.
    Модели: UserFavorites.
    Сериализаторы: FavoriteSerializer
    """
    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_favorites = get_object_or_404(UserFavorites, user=request.user)
        if serializer.validated_data.get('id') in user_favorites.favorites:
            user_favorites.favorites.remove(serializer.validated_data.get('id'))
            user_favorites.save()
        return Response({'success': 'Объявление успешно удалено из избранного'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def providing_a_payment_page(request):
    """
    Формирует запрос в эквайринг на предоставление страницы оплаты,
    в случае успеха перенаправляет пользователя на страницу оплаты.
    Сериализаторы: PaidSerializer
    """
    serializer = PaidSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        store_id = env_keys.get('PAID_SERVICE_STORE_ID')
        secret_key = env_keys.get('PAID_SERVICE_SECRET_KEY')
        url = env_keys.get('PAID_SERVICE_URL')
        user_email = request.user.email

        response = send_payment_request(url, store_id, secret_key, serializer, user_email)

        if response is None:
            return Response({"errors": {"connect": "Ошибка связи с банком. Пожалуйста, попробуйте позже!"}},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if response.status_code == 201:
            return Response({"redirect": response.json().get('checkout').get('redirect_url')})
        else:
            raise serializers.ValidationError(
                {"errors": {"connect": "Ошибка связи с банком. Пожалуйста, попробуйте позже!"}})
    else:
        raise serializers.ValidationError({"errors": serializer.errors})


@api_view(['GET', 'POST'])
def processing_successful_payment_for_services(request):
    """
    Webhook обрабатывающий успешную оплату услуг
    Модели: Service, Advertisement
    """
    transaction_data = request.data.get('transaction')
    try:
        if transaction_data:
            with transaction.atomic():
                additional = transaction_data.get('additional_data')
                services = Service.objects.all()
                keys_date_of_deactivate = {"vip": "date_of_deactivate_vip",
                                           "highlight_ad": "date_of_deactivate_highlight_ad",
                                           "special_accommodation": "date_of_deactivate_special_accommodation",
                                           "raise_in_search": "search_boost_date",
                                           "date_of_last_activation": "date_of_last_activation"}
                accommodation = {}
                paid_services = []
                for service in services:
                    if additional.get(service.key_word):
                        paid_services.append(service.service_name)
                        if service.key_word == "date_of_last_activation":
                            accommodation[keys_date_of_deactivate.get(service.key_word)] = datetime.now() + timedelta(
                                days=service.validity_period)
                            accommodation["date_of_deactivate"] = datetime.now() + timedelta(days=60)
                            accommodation["date_of_delete"] = datetime.now() + timedelta(days=180)
                            accommodation["search_boost_date"] = datetime.now()
                            accommodation["is_active"] = True
                        elif service.key_word == "raise_in_search":
                            accommodation[keys_date_of_deactivate.get(service.key_word)] = datetime.now() + timedelta(
                                days=service.validity_period)
                        elif service.key_word == "special_accommodation":
                            accommodation[service.key_word] = additional.get(service.key_word)
                            accommodation[keys_date_of_deactivate.get(service.key_word)] = datetime.now() + timedelta(
                                days=service.validity_period)
                            accommodation["search_boost_date"] = datetime.now()
                        else:
                            accommodation[service.key_word] = additional.get(service.key_word)
                            accommodation[keys_date_of_deactivate.get(service.key_word)] = datetime.now() + timedelta(
                                days=service.validity_period)

                Advertisement.objects.filter(id=additional.get('advertisement')).update(**accommodation)

                advertisement_title = request.data.get("transaction").get('additional_data').get("advertisement_title")

                run_send_email_task_celery('Оплата услуг на сайте Домер.бел',
                                           'asend_service.html',
                                           request.data.get("transaction").get("customer").get("email"),
                                           subject="Оплата услуг.",
                                           paid_services=paid_services,
                                           text=f"""Вы успешно оплатили на следующие услуги для объявления 
                                           "{advertisement_title}":"""
                                           )

                return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except:
        email = transaction_data.get("customer").get("email")
        advertisement_id = transaction_data.get('additional_data').get("advertisement")
        advertisement_title = transaction_data.get('additional_data').get("advertisement_title")
        run_send_email_task_celery('Оплата услуг на сайте Домер.бел',
                                   'asend_service.html',
                                   email,
                                   subject="Что-то пошло не так во время оплаты услуг.",
                                   text=f"""Если вы получили это сообщение, это значит что оплата прошла успешно, 
                                   но произошла ошибка во время обработки вашего объявления 
                                   "{advertisement_title}". 
                                   Если с вами не связались для решения этой проблемы, пожалуйста, свяжитесь с
                                   администрацией сайта через форму обратной связи или по номеру указанному на сайте."""
                                   )
        run_send_email_task_celery('Произошла ошибка во время оплаты услуг',
                                   'asend_notification.html',
                                   settings.EMAIL_HOST_USER,
                                   subject="Что-то пошло не так во время оплаты услуг",
                                   message=f"""У пользователя {email} возникла ошибка во время оплаты услуг
                                   для объявления "{advertisement_title}. Вероятно, оплата прошла, но услуги не 
                                   применились, свяжитесь с пользователем для решения этой проблемы.""",
                                   link=f"{reverse('admin:index')}advertisement/advertisement/{advertisement_id}/change/"
                                   )
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_region_list(request):
    """
    Возвращает список экземпляров модели Region.
    Модели: Region.
    Сериализаторы: RegionSerializer
    """
    regions = Region.objects.all()
    serializer = RegionSerializer(regions, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def get_list_of_cities(request, id):
    """
    Возвращает список дочерних экземпляров модели Region.
    Модели: Region.
    Сериализаторы: RegionSerializer
    """
    cities = Region.objects.filter(parent_id=id)
    serializer = RegionSerializer(cities, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_list(request):
    """
    Возвращает список экземпляров модели Category по родительскому id.
    Модели: Category.
    Сериализаторы: CategorySerializer
    """
    categories = Category.objects.filter(parent_id=request.query_params.get('id'))
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_subcategory_list(request):
    """
    Возвращает список экземпляров модели Category по-родительскому id
    и дополнительно данные из модели Field.
    Модели: Category.
    Сериализаторы: CategoryFieldsSerializer
    """
    categories = Category.objects.filter(parent_id=request.query_params.get('id')).prefetch_related(
        'field_set__spisok__element_set__elementtwo_set')
    serializer = CategoryFieldsSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_field_list(request):
    """
    Возвращает список экземпляров модели Field по id экземпляра модели Category
    и дополнительно данные из модели Spisok и Element.
    Модели: Field.
    Сериализаторы: FieldSerialier
    """
    fieldlist = Field.objects.filter(category_id=request.query_params.get('id')).select_related(
        'spisok').prefetch_related('spisok__element_set__elementtwo_set').order_by('id')
    serializer = FieldSerialier(fieldlist, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_element_list(request):
    """
    Возвращает список экземпляров модели Element по id экземпляра модели Field
    Модели: Element.
    Сериализаторы: ElementSerializer
    """
    elements = Element.objects.filter(spisok_id__field=request.query_params.get('id'))
    serializer = ElementSerializer(elements, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_elementtwo_list(request):
    """
    Возвращает список экземпляров модели ElementTwo
    по id экземпляра модели Element
    Модели: ElementTwo.
    Сериализаторы: ElementTwoSerializer
    """
    if request.query_params.get('slug') == 'undefined':
        return Response()
    else:
        elementstwo = ElementTwo.objects.filter(element_id=request.query_params.get('slug'))
        serializer = ElementTwoSerializer(elementstwo, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_store_list_by_user(request):
    """
    Возвращает список магазинов пользователя.
    Модели: Store.
    Сериализаторы: StoreSerializer
    """
    stores = Store.objects.filter(user=request.user.id)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def get_bulk_import_of_ads(request):
    """
    Функция проверяет возможность открытия файлв и запускает задачу в celery по его обработки
    """
    serializer = UploadFileSerializer(data=request.data)
    if serializer.is_valid():
        if serializer.validated_data.get("file").name.endswith('xlsx'):
            # Работа с электронной таблицей
            try:
                upload_file = serializer.validated_data.get("file")
                book = openpyxl.open(upload_file, read_only=True)
                save_file = UploadFile(file=upload_file, user=request.user)
                save_file.save()
                ads = save_many_ads_from_excel_task.delay(upload_file=f'./media/{save_file.file.name}',
                                                          id=request.user.id,
                                                          first_name=request.user.first_name,
                                                          phone_number=request.user.phone_number,
                                                          email=request.user.email)

                return Response({'task_id': f'{ads.task_id}'})
            except:
                # логируем ошибку
                # logger.warning(f'user: {request.user}, action:bulk ads from file, error: incorrect file format')
                return Response({'error': 'Невозможно прочитать файл.'})

        elif serializer.validated_data.get("file").name.endswith('zip'):
            # Работа с электронным архивом
            try:
                upload_zip = serializer.validated_data.get("file")
                with ZipFile(upload_zip, 'r') as zip:
                    files_from_zip = zip.namelist()
                save_zip = UploadFile(file=upload_zip, user=request.user)
                save_zip.save()
                ads = save_many_ads_from_zip_task.delay(upload_zip=f'./media/{save_zip.file.name}',
                                                        id=request.user.id,
                                                        first_name=request.user.first_name,
                                                        phone_number=request.user.phone_number,
                                                        email=request.user.email)
                return Response({'task_id': f'{ads.task_id}'})
            except:
                # логируем ошибку
                # logger.warning(f'user: {request.user}, action:bulk ads from file, error: unable to open file')
                return Response({'error': 'Невозможно прочитать файл.'})
    else:
        # логируем ошибку
        # logger.warning(f'user: {request.user}, action:bulk ads from file, error: incorrect file format')
        return Response({'error': 'Ошибка при загрузке файла. Убедитесь, что загружаемый файл необходимого расширения'})


@api_view(["GET", "POST"])
def get_result_task(request, id):
    """
    Возвращает прогресс выполнения задачи массового импорта объявлений и её результат
    """
    task = app.AsyncResult(id=id)
    if task.state == "SUCCESS":
        return JsonResponse({'state': task.state, 'result': task.result})
    else:
        return JsonResponse({'state': task.state})
