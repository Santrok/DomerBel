from django.urls import path

from paid_service.views import test_paid, send_paid, get_bepaid

urlpatterns = [
    path('test_paid/', test_paid, name='test_paid'),
    path('api/send_paid/', send_paid),
    path('api/notification/', get_bepaid)
]