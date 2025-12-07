from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('auth/', include('authentication.urls')),
        path('users/', include('users.urls')),
        path('players/', include('players.urls')),
        path('offers/', include('offers.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
