from django.contrib import admin

from .models import *


class BeatmapEntryInline(admin.TabularInline):
    model = BeatmapEntry


class CommentInline(admin.StackedInline):
    model = Comment


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [
        BeatmapEntryInline,
        CommentInline
    ]


admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(RatingLog)
admin.site.register(Beatmap)
admin.site.register(BeatmapEntry)
