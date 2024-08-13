from drf_recaptcha.fields import ReCaptchaV2Field
from rest_framework import serializers


from advertisement.models import Region, Category, Field, Spisok, ElementTwo, Element, Advertisement, Store
from api_domer.validators import validate_password, validate_phone
from main_page_domer.models import ReasonOfComplaint, Complaint
from users.models import User


class GetListOfCitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class GetListOfCategoriesSerializer(serializers.ModelSerializer):
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


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'title']


class PhotoAdvertisementSerializer(serializers.Serializer):
    InMemoryUploadedFile = serializers.ImageField()


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['article', 'title', "price",
                  'category', 'bearer', 'region',
                  'preview_image', 'contact_name',
                  'email', 'phone_num', 'description',
                  'video_link', 'store']


class AdditionalInformationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    error = serializers.CharField()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(required=True, validators=[validate_password], write_only=True)
    phone_number = serializers.CharField(validators=[validate_phone])

    recaptcha = ReCaptchaV2Field(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'entity', 'phone_number', 'password', 'password2', 'recaptcha']

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('recaptcha')
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError({"password":["Введенные пароли не совпадают"], "password2":[""]})
        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, error_messages={'blank': 'Обязательное поле'})
    password = serializers.CharField(write_only=True, error_messages={'blank': 'Обязательное поле'})


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, error_messages={'blank': 'Обязательное поле'})
    recaptcha = ReCaptchaV2Field(write_only=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким Email не найден")
        else:
            return email


class FavoriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetListOfCategoriesFieldsSerializer(serializers.ModelSerializer):
    field_set = FieldSerialier(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'field_set']


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
