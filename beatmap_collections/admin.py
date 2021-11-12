"""
Add beatmap database model to admin page.
"""
from django.contrib import admin
from .models import *


class BeatmapEntryInline(admin.TabularInline):
    """Creat BeatmapEntryInline model."""
    model = BeatmapEntry


class CommentInline(admin.StackedInline):
    """Creat CommentInline model."""
    model = Comment


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Add Collection to admin page."""
    inlines = [
        BeatmapEntryInline,
        CommentInline
    ]


admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(RatingLog)
admin.site.register(Beatmap)
admin.site.register(BeatmapEntry)
