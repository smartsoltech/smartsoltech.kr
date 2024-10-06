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
    path('create_order/<int:pk>/', views.create_order, name='create_order'),
    path('about/', views.about_view, name="about_view"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)