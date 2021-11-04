"""Models for the beatmap collections app."""

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone

FALLBACK_USER_KEY = 1


class Collection(models.Model):
    """This model represents a collection. It contains the metadata of the collection.

    Attributes:
        collection_list: The thumbnail of this collection
        name: The name of this collection
        author: The user who created this collection.
        description: The description of this collection.
        beatmap_count: The number of beatmaps contained in this collection.
        tags: This collection's tag(s).
        create_date: The creation date of this collection.
        edit_date: The date that this collection was last modified.
    """

    collection_list = models.ImageField(default="collection_list/placeholder.jpg", upload_to='collection_list',
                                        validators=[FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg',
                                                                                               'jpeg', 'bmp', 'svg',
                                                                                               'webp'])])
    name = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=FALLBACK_USER_KEY)
    description = models.CharField(max_length=250, blank=True)
    tags = models.TextField(default="Pending", blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the name of the Collection model."""
        return self.name

    def save(self, *args, **kwargs):
        """Overrides the save method to optimize the collection_list picture size."""
        super().save(*args, **kwargs)
        cover_image = Image.open(self.collection_list.path)
        if cover_image.height > 1080 or cover_image.width > 1920:
            cover_image.thumbnail((1920, 1080))
            cover_image.save(self.collection_list.path)
    
    @property
    def beatmaps_count(self):
        """Count beatmaps in the collection."""
        return BeatmapEntry.objects.filter(collection=self, owner_approved=True).count()


class Comment(models.Model):
    """This model represents a comment made to a collection. It contains the metadata of the comment.

    Attributes:
        collection: The collection this comment was posted on.
        user: The User who posted this comment.
        detail: The text of this comment.
        create_date: The date this comment was posted.
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=FALLBACK_USER_KEY)
    detail = models.CharField(max_length=250)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the name of the Comment model."""
        try:
            return f"Comment from {self.user.username} in {self.collection.name}"
        except AttributeError:
            return f"Unknown comment"


class Rating(models.Model):
    """This model stores the rating information of a collection.

    Attributes:
        collection: The collection this rating data belongs to.
        rating: The rating of a collection.
        count: The number people who rated the collection.
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    count = models.IntegerField(default=0)


class RatingLog(models.Model):
    """This model represents a single rating made by a user. It contains the metadata of the rating.

    Attributes:
        collection: The collection this rating belongs to.
        user: The user who made this rating.
        user_rating: The score that the user gave.
        create_date: The date when this rating was made.
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=FALLBACK_USER_KEY)
    user_rating = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)


class Beatmap(models.Model):
    """This model represents a beatmap. It contains the beatmap's metadata.

    Attributes:
        beatmap_id: An identification number of this beatmap.
        beatmapset_id: An identification number of the beatmap set that this beatmap is in.
        bpm: The number of beats per minute this beatmap offers.
        count_normal: The number of total normal note in the beatmap.
        count_slider: The number of total normal slider or the long note in the beatmap.
        count_spinner: The number of total spinner in the beatmap.
        difficultyrating: The difficulty of this beatmap. It is represented as a star rating (SR).
        diff_approach: The approach rate (AR) value of the beatmap.
        diff_drain: The Health drain (HP) value of the beatmap.
        diff_overall: The Overall difficulty (OD) value of the beatmap.
        diff_size: The Circle size value (CS) of the beatmap. This value mainly use in the beatmap in osu! mode.
        diff_aim: The aim value of the beatmap. Normally available only on osu! mode.
        diff_speed: The speed value of the beatmap. Normally available only on osu! mode.
        max_combo: The maximum combo a user can reach playing this beatmap.
        playcount: The number of times this beatmap is played.
        favourite_count: The number of people who added this beatmap is added as one of their favourites.
        total_length: The total length of this beatmap (its playtime).
        mode: The mode ID of the beatmap.
        title: The name of this beatmap.
        artist: This beatmap's music composer.
        source: The source for this beatmap's song.
        creator: The name of the user who created this beatmap.
        creator_id: The identification number of the user who created this beatmap.
        genre_id: The genre ID of this beatmap.
        language_id: The language ID of this beatmap.
        approved: The approval status of this beatmap. There are 7 types in total:
                    1) 4 Loved
                    2) 3 Qualified
                    3) 2 Approved
                    4) 1 Ranked
                    5) 0 Pending
                    6) -1 WIP
                    7) -2 Graveyard
        version: The version or the difficulty name of this beatmap.
        url: The direct link to this beatmap.
        beatmap_card: The cover art of this beatmap.
        beatmap_list: The thumbnail of this beatmap.
        tags: This beatmap's tag(s). If it have more than 1 tag it will separate with space.
        submit_date: The date this beatmap was submitted.
        approved_date: The date this beatmap was ranked.
        last_update: The date this beatmap was last updated. May be after approved_date if map was unranked and reranked.
        collection: The collection that this beatmap is included.
    """
    beatmap_id = models.IntegerField(default=75)
    beatmapset_id = models.IntegerField(default=1)

    title = models.CharField(default="DISCO PRINCE", max_length=100)
    artist = models.CharField(default="Kenji Ninuma", max_length=100)
    source = models.CharField(default="", max_length=100, blank=True)
    creator = models.CharField(default="peppy", max_length=100)
    approved = models.CharField(default="1", max_length=10)
    difficultyrating = models.FloatField(default="2.39774")
    bpm = models.CharField(default="119.999", max_length=10)
    version = models.CharField(default="Normal", max_length=50, blank=True)

    url = models.URLField(default="https://osu.ppy.sh/beatmapsets/1#osu/75")

    beatmap_card = models.ImageField(default='default_beatmap_cover.jpeg', upload_to='beatmap_card', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])
    beatmap_list = models.ImageField(default='default_beatmap_thumbnail.jpeg', upload_to='beatmap_list', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg', 'webp'])])

    # New attributes starts here.
    count_normal = models.IntegerField(default=0)
    count_slider = models.IntegerField(default=0)
    count_spinner = models.IntegerField(default=0)

    diff_approach = models.FloatField(default="0.0")
    diff_drain = models.FloatField(default="0.0")
    diff_overall = models.FloatField(default="0.0")
    diff_size = models.FloatField(default="0.0")
    diff_aim = models.FloatField(default="0.0")
    diff_speed = models.FloatField(default="0.0")

    max_combo = models.IntegerField(default=0)
    playcount = models.IntegerField(default=0)
    favourite_count = models.IntegerField(default=0)
    total_length = models.IntegerField(default=0)
    mode = models.IntegerField(default=0)
    creator_id = models.IntegerField(default=0)
    genre_id = models.IntegerField(default=0)
    language_id = models.IntegerField(default=0)
    tags = models.CharField(max_length=5000, blank=True)

    submit_date = models.DateTimeField(default=timezone.now)
    approved_date = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} [{self.version}]"


class BeatmapEntry(models.Model):
    """This model acts as a pointer to a beatmap.

    Attributes:
        collection: The collection that the model BeatmapEntry is pointing to is in.
        beatmap: The beatmap that BeatmapEntry is pointing to.
        author: The user who suggested this beatmap.
        comment: The comment to why the beatmap should be added.
        add_date: The date when the beatmap was added to the collection.
        user: The User who posted this beatmap.
        description: The description of this beatmap that users write it when adding the beatmap.
        owner_approved: The collection approval status of this beatmap. Changes to true if the owner of the requested
                        collection approves the request to add this beatmap.
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True)
    beatmap = models.ForeignKey(Beatmap, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=FALLBACK_USER_KEY, related_name="author")
    comment = models.CharField(max_length=250)
    add_date = models.DateTimeField(auto_now_add=True)

    # Fields originally from Beatmap model.
    owner_approved = models.BooleanField(default=False)

    def __str__(self):
        try:
            return f"{self.beatmap.title} [{self.beatmap.version}] in {self.collection.name}"
        except AttributeError:
            return f"Unknown beatmap in unknown collection"
