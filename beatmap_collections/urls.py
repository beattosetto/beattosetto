from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.create_collection, name='new_collection'),
    path('title/', views.collection_page, name='collection_title'),
    path('add/beatmap', views.add_beatmap, name='add_beatmap'),
    path('edit/', views.edit_collection, name='edit_collection')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
