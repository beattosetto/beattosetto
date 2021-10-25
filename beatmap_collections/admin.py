from django.contrib import admin
from .models import *

admin.site.register(Collection)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(RatingLog)
admin.site.register(Beatmap)
admin.site.register(Profile)
admin.site.register(BeatmapEntry)
