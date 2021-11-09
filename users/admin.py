"""
This admin.py manage about the profile for adding to admin page.
"""
from django.contrib import admin
from .models import *

admin.site.register(Profile)
