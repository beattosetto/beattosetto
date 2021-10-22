from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('new/', views.create_collection_page, name='new_collection'),
    path('new/<str:error>/', views.create_collection_page, name='new_collection'),
    path('save/', views.save_collection, name='save_collection')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
