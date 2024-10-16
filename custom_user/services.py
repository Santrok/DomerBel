from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def make_activation_url_for_reset_password(user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

    return activation_url
