from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('', include('profile.urls')),
    path('set_language/', set_language, name='set_language'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

