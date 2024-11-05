from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from advertisement.models import AdvertisementSitemap

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

sitemaps = {
    'advertisement': AdvertisementSitemap,
}

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap",),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("__debug__/", include("debug_toolbar.urls")),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('advertisement/', include('advertisement.urls')),
    path('personal_account/', include('personal_account.urls')),
    path('stores/', include('store.urls')),
    path('publications/', include('publication.urls')),
    path('api/v1/', include('api.urls')),
    path('user/', include('custom_user.urls')),
    path('chat/', include('chat.urls')),
    path('paid_service/', include('paid_service.urls')),
    path('related_data/', include('related_data.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
