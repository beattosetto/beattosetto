"""
File contain url path for users app.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
]
