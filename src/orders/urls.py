from django.urls import re_path

from . import views

app_name = 'orders'

urlpatterns = [
    re_path(r'^cart-add/$', views.add_to_cart_view, name='cart-add'),
    re_path(r'^check-discount/$', views.check_discount_code_view, name='check-discount'),
    re_path(r"^mylist/$", views.my_orders_view, name='mylist'),
    re_path(r'^management/$', views.order_manage_view, name='management'),
    re_path(r'^order-add/$', views.my_orders_view, name='order-add'),
    re_path(r'^(?P<order_id>[0-9A-Za-z]+)/$', views.order_detail_view, name='detail'),
    re_path(r'^(?P<order_id>[0-9A-Za-z]+)/delete/$', views.delete_order_view, name='delete'),
    re_path(r'^(?P<order_id>[0-9A-Za-z]+)/update-status/$', views.update_status_view, name='update-status'),
    re_path(r'^(?P<order_id>[0-9A-Za-z]+)/update-visibility/$', views.update_visibility_view, name='update-visibility'),
    re_path(r'^(?P<order_id>[0-9A-Za-z]+)/update-payment-status/$', views.update_payment_status_view,
            name='update-payment-status'),
]
