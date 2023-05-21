# from django.urls import path, include, re_path
# from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # re_path(r'^$', index_view, name='homepage'),
    # re_path(r'^404notfound/', error_404_view, name='404NotFound'),
    # url(r'^500servererror/', error_500_view, name='error500'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
