from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('users/<int:user_id>/', views.profile, name='profile_collections'),
]