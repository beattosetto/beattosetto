"""
This admin.py manage about admin register the profile.
"""
from django.contrib import admin
from .models import *

admin.site.register(Profile)
