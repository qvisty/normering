from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("skoleadmin/", admin.site.urls, name="skoleadmin"),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("skole.urls")),
    path("sliders/", include("sliders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)