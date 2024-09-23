from rest_framework import serializers

from advertisement.models import Advertisement
from paid_service.models import Service


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
