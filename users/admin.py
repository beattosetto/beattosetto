"""
Add users database model to admin page.
"""
from django.contrib import admin

from .models import *

admin.site.register(Profile)
