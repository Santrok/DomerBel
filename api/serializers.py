from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from drf_recaptcha.fields import ReCaptchaV2Field
from rest_framework import serializers

from advertisement.models import ReasonOfComplaint, Complaint, Advertisement
from paid_service.models import Service
from related_data.models import Region, Category, ElementTwo, Element, Spisok, Field
from store.models import Store
from utils.validators import validate_phone
from .validators import validate_password


class ReasonOfComplaintSerializer(serializers.Serializer):
    class Meta:
        model = ReasonOfComplaint
        fields = '__all__'


class ComplaintSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(required=True)
    recaptcha = ReCaptchaV2Field(write_only=True)

    class Meta:
        model = Complaint
        fields = ['reason', 'text', 'user', 'advertisement', 'recaptcha']

    def create(self, validated_data):
        validated_data.pop('recaptcha')
        return Complaint.objects.create(**validated_data)

    def validate(self, data):
        data['user'] = data.get('user').lower()
        return data


class AdvertisementSerializer(serializers.ModelSerializer):
    photo = serializers.ListField(child=serializers.ImageField(), allow_null=True,
                                  allow_empty=True, max_length=30, required=False,
                                  error_messages={'max_length': 'Убедитесь, что в этом поле не более 30 элементов.'})

    class Meta:
        model = Advertisement
        fields = ['article', 'title', "price",
                  'category', 'bearer', 'region',
                  'preview_image', 'contact_name',
                  'email', 'phone_num', 'description',
                  'video_link', 'store', 'photo']


class AdditionalInformationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    error = serializers.CharField()


class UserMessageSerializer(serializers.Serializer):
    chat_object = serializers.IntegerField()
    text_message = serializers.CharField()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(required=True, validators=[validate_password], write_only=True)
    phone_number = serializers.CharField(validators=[validate_phone])
    recaptcha = ReCaptchaV2Field(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'entity', 'phone_number', 'password', 'password2', 'recaptcha']

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('recaptcha')
        return get_user_model().objects.create_user(**validated_data)

    def validate(self, data):
        email = data.get('email').lower()
        data['email'] = email
        password = data.get('password')
        password2 = data.get('password2')
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": ["Пользователь с таким Email уже существует"]})
        if password != password2:
            raise serializers.ValidationError({"password": ["Введенные пароли не совпадают"], "password2":[""]})
        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, error_messages={'blank': 'Обязательное поле'})
    password = serializers.CharField(write_only=True, error_messages={'blank': 'Обязательное поле'})

    def validate(self, data):
        data['email'] = data.get('email').lower()
        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, error_messages={'blank': 'Обязательное поле'})
    recaptcha = ReCaptchaV2Field(write_only=True)

    def validate(self, data):
        data['email'] = data.get('email').lower()
        return data


class FavoriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class PaidSerializer(serializers.Serializer):
    advertisement = serializers.IntegerField()
    services = serializers.ListField(child=serializers.IntegerField(),
                                     error_messages={'required': 'Выберите хотя бы одну услугу'})

    def validate_advertisement(self, advertisement):
        try:
            advertisement = Advertisement.objects.get(id=advertisement,
                                                      author=self.context.get('request').user)
            return advertisement
        except:
            raise serializers.ValidationError("Объявление не найдено")

    def validate_services(self, services):
        services = Service.objects.filter(id__in=services)
        if services:
            return services
        else:
            raise serializers.ValidationError("Выберите хотя бы одну услугу")


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ElementTwoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementTwo
        fields = 'title',


class ElementSerializer(serializers.ModelSerializer):
    elementtwo_set = ElementTwoSerializer(many=True, read_only=True)

    class Meta:
        model = Element
        fields = 'id', 'title', 'elementtwo_set'


class SpisokSerializer(serializers.ModelSerializer):
    element_set = ElementSerializer(many=True, read_only=True)

    class Meta:
        model = Spisok
        fields = 'title', 'element_set'


class FieldSerialier(serializers.ModelSerializer):
    spisok = SpisokSerializer(read_only=True)

    class Meta:
        model = Field
        fields = '__all__'


class CategoryFieldsSerializer(serializers.ModelSerializer):
    field_set = FieldSerialier(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'field_set']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'title']


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'zip'])])
