from django.urls import re_path
from .views import *

app_name = 'restaurants'

urlpatterns = [
    re_path(r'^$', restaurant_list, name='list'),
    re_path(r'^(?P<slug>[\w-]+)/$', restaurant_detail, name='detail'),
]
