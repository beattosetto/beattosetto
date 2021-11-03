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
    path('managemap/', views.manage_beatmap, name='manage_beatmap'),
    path('collections/<int:collection_id>/approval', views.beatmap_approval, name='beatmap_approval'),
    path('collections/<int:collection_id>/approve/<int:beatmap_entry_id>', views.approve_beatmap, name='approve_beatmap'),
    path('collections/<int:collection_id>/deny/<int:beatmap_entry_id>', views.deny_beatmap, name='deny_beatmap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
