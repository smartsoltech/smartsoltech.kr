# web/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('client/<int:pk>/', views.client_detail, name='client_detail'),
    path('blog/<int:pk>/', views.blog_post_detail, name='blog_post_detail'),
    path('services/', views.services_view, name='services'),
    # path('create_order/<int:pk>/', views.create_order, name='create_order'),
    path('about/', views.about_view, name="about_view"),
    path('service/generate_qr_code/<int:service_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('service/request_status/<int:service_id>/', views.request_status, name='request_status'),
    path('service/request/<int:service_id>/', views.create_service_request, name='create_service_request'),
    path('complete_registration/<int:request_id>/', views.complete_registration, name='complete_registration'),
    path('complete_registration/', views.complete_registration_basic, name='complete_registration_basic'),
    path('service/check_service_request_data/', views.check_service_request_data, name='check_service_request_data'),
    path('client/orders/', views.client_orders, name='client_orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('service/send_telegram_notification/', views.send_telegram_notification, name='send_telegram_notification'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)