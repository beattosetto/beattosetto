"""
File contain url path for actions app.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('actions/', views.actions, name='actions'),
    path('actions/update_beatmap', views.update_beatmap_action, name='actions_update_beatmap'),
    path('action/action_log/<int:log_id>', views.check_action_log, name='check_action_log'),
    path('action/delete/<int:log_id>', views.delete_action_log, name='delete_action_log')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
