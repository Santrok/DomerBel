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

from advertisement.models import Region, Category, Field, ElementTwo, PhotoAdvertisement, Advertisement, Store, Element
from api_domer.serializers import GetListOfCitiesSerializer, GetListOfCategoriesSerializer, FieldSerialier, \
    ElementTwoSerializer, AdvertisementSerializer, StoreSerializer, \
    UserRegisterSerializer, UserLoginSerializer, PasswordResetSerializer, \
    FavoriteSerializer, ElementSerializer, GetListOfCategoriesFieldsSerializer, ReasonOfComplaintSerializer, \
    ComplaintSerializer, MessageSerializer

from api_domer.utils import validate_additional_information
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


# Отдает список дочерних категорий по родительскому id (для поиска магазиноа и поиска в ЛК)
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
    serializer = AdvertisementSerializer(data=request.data)
    serializer.is_valid()
    keys_to_delete = ['csrfmiddlewaretoken', 'preview_img', 'photo_files']
    keys_to_delete.extend(serializer.data.keys())
    serializer_additional_error, additional_information = validate_additional_information(keys_to_delete,
                                                                                          additional_information)
    if serializer.is_valid() and not serializer_additional_error.data:
        additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')
        for i in additional_information_save:
            additional_information[i.title] = ', '.join(additional_information.pop(f'{i.id}'))
        new_advertisement = Advertisement(author=None if request.user.is_anonymous else request.user,
                                          additional_information=additional_information,
                                          **serializer.validated_data)
        new_advertisement.save()
        if request.data.getlist('photo_files') != ['']:
            for photo in request.data.getlist('photo_files'):
                if photo.name == request.data.get("preview_img"):
                    new_advertisement.preview_image = photo
                    new_advertisement.save()
                else:
                    additional_photo = PhotoAdvertisement(photo=photo, advertisement=new_advertisement)
                    additional_photo.save()
        return Response({"success": "<p>Ваше объявление отправлено на модерацию.</p><p>После модерации оно появится в списке объявлений.</p>",
                         "link": f"{env_keys.get('URL')}", "link_text": "Вернуться на главную"}, status=status.HTTP_201_CREATED)
    else:
        raise serializers.ValidationError(
            {"error_additional": serializer_additional_error.data, "error": serializer.errors})


@api_view(['PATCH'])
def update_advertisement(request):
    additional_information = dict(request.data.copy())
    serializer = AdvertisementSerializer(data=request.data)
    serializer.is_valid()
    keys_to_delete = ['csrfmiddlewaretoken', 'preview_img', 'photo_files', 'deleted_images', 'advertisement']
    keys_to_delete.extend(serializer.data.keys())
    serializer_additional_error, additional_information = validate_additional_information(keys_to_delete,
                                                                                          additional_information)
    if serializer.is_valid() and not serializer_additional_error.data:
        additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')
        for i in additional_information_save:
            additional_information[i.title] = ', '.join(additional_information.pop(f'{i.id}'))
        deleted_images = request.data.get('deleted_images').split(',')
        preview_img = request.data.get("preview_img")
        Advertisement.objects.filter(author=request.user, id=request.data.get('advertisement')
                                     ).update(moderated=False, additional_information=additional_information,
                                              **serializer.validated_data)
        advertisement = get_object_or_404(Advertisement, id=request.data.get('advertisement'))

        if request.data.getlist('photo_files') != ['']:
            for photo in request.data.getlist('photo_files'):
                if photo.name == preview_img:
                    if advertisement.preview_image not in deleted_images:
                        PhotoAdvertisement.objects.create(photo=advertisement.preview_image,
                                                          advertisement=advertisement)
                    advertisement.preview_image = photo
                    advertisement.save()
                    preview_img = advertisement.preview_image
                else:
                    additional_photo = PhotoAdvertisement(photo=photo, advertisement=advertisement)
                    additional_photo.save()

        if advertisement.preview_image != preview_img:
            if advertisement.preview_image not in deleted_images:
                PhotoAdvertisement.objects.create(photo=advertisement.preview_image,
                                                  advertisement=advertisement)
            if preview_img:
                advertisement.preview_image = preview_img
                inst = get_object_or_404(PhotoAdvertisement, photo=preview_img)
                PhotoAdvertisement.objects.filter(id=inst.id).update(photo=None)
                PhotoAdvertisement.objects.filter(id=inst.id).delete()
            else:
                advertisement.preview_image = None
            advertisement.save()

        if request.data.getlist('deleted_images'):
            PhotoAdvertisement.objects.filter(photo__in=deleted_images).delete()

        return Response({"success": "<p>Ваше объявление отправлено на модерацию.</p><p>После модерации оно появится в списке объявлений.</p>",
                         "link": f"{env_keys.get('URL')}/users/personal_account/", "link_text": "В мой кабинет"}, status=status.HTTP_201_CREATED)
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
            raise serializers.ValidationError({"errors": {"email": "Пользователь не найден. Проверьте правильность введенных данных.", "password": ''}})
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
    '''Отадет элементы связанные с полем по id'''
    elements = Element.objects.filter(spisok_id__field=request.query_params.get('id'))
    serializer = ElementSerializer(elements, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_subcategory_list(request):
    '''Отдает подкатегориии и их поля по id категории'''
    categories = Category.objects.filter(parent_id=request.query_params.get('id')).prefetch_related('field_set__spisok__element_set__elementtwo_set')
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

        # try:
        #     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
        # except smtplib.SMTPException as error:
        #     return Response({'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Ваша жалоба на объявление отправлена администрации сайта'},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors})


@api_view(['POST'])
def create_chat(request):
    print(1)
    serializer = MessageSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        print(serializer.validated_data)
        print(2)
        advertisement = get_object_or_404(Advertisement, id=serializer.validated_data.get('advertisement'))
        print(3)
        chat = Chat.objects.filter(advertisement=advertisement, members__in=[request.user, advertisement.author_id])
        print(4)
        if not chat:
            chat = Chat.objects.create(advertisement=advertisement)
            chat.members.set([request.user.id, advertisement.author_id])
            Message.objects.create(chat=chat, author=request.user, message=serializer.validated_data.get('text_message'))
        else:
            Message.objects.create(chat=chat[0], author=request.user,
                                   message=serializer.validated_data.get('text_message'))

        return Response({'success': 'Ваше сообщение отправлено'}, status=status.HTTP_201_CREATED)
    else:
        return Response({"errors": serializer.errors})