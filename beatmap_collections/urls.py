from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views, views_api

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.create_collection, name='new_collection'),
    path('collections/<int:collection_id>/', views.collection_page, name='collection'),
    path('collections/<int:collection_id>/add/beatmap', views.add_beatmap, name='add_beatmap'),
    path('collections/<int:collection_id>/edit', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/manage/', views.manage_beatmap, name='manage_beatmap'),
    path('collections/<int:collection_id>/approval', views.beatmap_approval, name='beatmap_approval'),
    path('collections/<int:collection_id>/approve/<int:beatmap_entry_id>', views.approve_beatmap, name='approve_beatmap'),
    path('collections/<int:collection_id>/deny/<int:beatmap_entry_id>', views.deny_beatmap, name='deny_beatmap'),
    path('collections/<int:collection_id>/delete/<int:beatmap_entry_id>', views.delete_beatmap, name='delete_beatmap'),
    path('tag/<str:tag>', views.collections_by_tag, name='collection_by_tag'),
    path('api/get_demo_card/<int:beatmap_id>', views_api.live_beatmap_card, name='get_demo_card'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
