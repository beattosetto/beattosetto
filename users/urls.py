"""
This urls.py manage about redirect path in urlpattern.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('settings/', views.settings, name='settings'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
]
