import smtplib

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.decorators import api_view
from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from advertisement.models import (Region, Category, Field, ElementTwo, Advertisement, Store, Element)
from api_domer.serializers import (GetListOfCitiesSerializer, GetListOfCategoriesSerializer, FieldSerialier,
                                   ElementTwoSerializer, AdvertisementSerializer, StoreSerializer,
                                   UserRegisterSerializer, UserLoginSerializer, PasswordResetSerializer,
                                   FavoriteSerializer, ElementSerializer, GetListOfCategoriesFieldsSerializer,
                                   ReasonOfComplaintSerializer, ComplaintSerializer, MessageSerializer)
from api_domer.tasks import save_advertisement_task, update_advertisement_task

from api_domer.utils import validate_additional_information, save_temp_photo
from config import settings
from config.settings import env_keys
from main_page_domer.models import ReasonOfComplaint
from users.models import User, UserFavorites, Chat, Message


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
        photo_list = data.pop('photo', None)

        # Временно сохраняем фотографии что-бы переделать их адреса в celery
        processed_photo = save_temp_photo(photo_list, request.data.get("preview_img")) if photo_list else None

        # Вызываем задачу celery для сохранения объявлений
        save_advertisement_task.delay(request.user.id, data, additional_information, processed_photo)

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
        new_photo_list = data.pop('photo', [])
        preview_photo = request.data.get('preview_img')
        deleted_photo = request.data.get('deleted_images').split(',') if request.data.get('deleted_images') else None

        # Проверка, изменилось ли главное изображение
        if advertisement.preview_image != preview_photo and preview_photo not in [i.name for i in new_photo_list]:
            new_preview_photo_from_old_ones = preview_photo
        else:
            new_preview_photo_from_old_ones = None

        # Временно сохраняем новые фотографии что-бы переделать их адреса в celery
        processed_photo = save_temp_photo(new_photo_list,
                                          request.data.get("preview_img")) if new_photo_list != [] else None

        # Вызываем задачу celery для сохранения объявлений
        update_advertisement_task.delay(request.user.id, request.data.get('advertisement'), data,
                                        additional_information, processed_photo, new_preview_photo_from_old_ones,
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
        send_mail(
            subject='Восстановление пароля',
            message=f'''
            Вы получили это письмо, потому что Вы (или кто-то другой) запросили восстановление пароля от учётной записи 
            на сайте {url}, которая связана с этим адресом электронной почты.
            
            Для восстановления пароля перейдите по данной ссылке: 
            
            {url}{activation_url}
            
            Спасибо, что используете наш сайт!
            
            Команда сайта {url}
            
            
            Если вы не запрашивали восстановление пароля, то проигнорируйте это сообщение''',
            from_email=None,
            recipient_list=[email],
            fail_silently=False)
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

        subject = f'Жалоба от пользователя {user} на объявление  id={advertisement.id}. Причина: {reason} '
        message = text

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
        except smtplib.SMTPException as error:
            return Response({'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Ваша жалоба на объявление отправлена администрации сайта'},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors})


@api_view(['POST'])
def create_chat(request):
    serializer = MessageSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        chat_object = {}
        if request.data.get('advertisement'):
            advertisement = get_object_or_404(Advertisement, id=serializer.validated_data.get('chat_object'))
            chat_object['advertisement'] = advertisement
            chat_object['members'] = advertisement.author_id
        elif request.data.get('store'):
            store = get_object_or_404(Store, id=serializer.validated_data.get('chat_object'))
            chat_object['store'] = store
            chat_object['members'] = store.user_id
        chat = Chat.objects.filter(**chat_object).filter(members=request.user)
        if not chat:
            any_member = chat_object.pop('members', None)
            chat = Chat.objects.create(**chat_object)
            chat.members.set([request.user.id, any_member])
            Message.objects.create(chat=chat, author=request.user,
                                   message=serializer.validated_data.get('text_message'))
        else:
            Message.objects.create(chat=chat[0], author=request.user,
                                   message=serializer.validated_data.get('text_message'))

        return Response({'success': 'Ваше сообщение отправлено'}, status=status.HTTP_200_OK)
    else:
        return Response({"errors": serializer.errors})
