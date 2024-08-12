from advertisement.models import Field
from api_domer.serializers import AdditionalInformationSerializer


def validate_additional_information(keys_to_delete, additional_information):
    for key in keys_to_delete:
        if key in additional_information:
            del additional_information[key]
    key_error = []
    for i in additional_information:
        if '' in additional_information.get(i):
            key_error.append(i)
    additional_information_filter = Field.objects.filter(id__in=key_error).exclude(error='')
    serializer_additional_error = AdditionalInformationSerializer(data=additional_information_filter, many=True)
    serializer_additional_error.is_valid()
    return serializer_additional_error, additional_information