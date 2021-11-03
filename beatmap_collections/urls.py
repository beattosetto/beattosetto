from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.create_collection, name='new_collection'),
    path('collections/<int:collection_id>/', views.collection_page, name='collection'),
    path('collections/<int:collection_id>/add/beatmap', views.add_beatmap, name='add_beatmap'),
    path('collections/<int:collection_id>/edit', views.edit_collection, name='edit_collection'),
    path('users/<int:user_id>/', views.list_collection_from_user, name='profile_collections')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
