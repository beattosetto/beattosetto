from unittest import skip
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.http import HttpRequest
from django.urls import reverse

from .models import *
from .forms import *
from django.db import models
from .functions import *
import io

from .templatetags.convert_progress_bar import convert_progress_bar
from .templatetags.convert_star_rating import convert_star_rating
from .templatetags.count_beatmaps import count_beatmaps
from .templatetags.length_format import length_format
from .templatetags.thousand_seperator import thousand_seperator


def create_collection(name, user=None) -> Collection:
    """Utility function for creating collection.

    The test user will have both username and password set to "test".
    """
    if user is None:
        user, _ = User.objects.get_or_create(username="test")
        user.set_password("test")
    return Collection.objects.create(author=user, name=name)


class CreateCollectionViewTests(TestCase):
    """Tests for the create_collection_page view."""

    def test_login_user_only(self):
        """If the user is not logged in they can't access the page."""
        user = User.objects.create(username="GordonFreeman")
        user.set_password('12345')
        user.save()

        # Test logged in.
        self.client.login(username='GordonFreeman', password='12345')
        response = self.client.get('/new/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('beatmap_collections/create_collection.html')
        # Test logged out.
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/accounts/login/?next=/new/')


class CollectionCreateViewTest(TestCase):
    """Tests for the create collection by form and its value after create."""

    def test_form_valid_with_image_missing(self):
        """Test the create collection form is valid despite the collection image field is missing."""
        collection_form_data = {'collection_list': '',
                                'name': 'Test',
                                'description': 'This is test'}

        collection_form = CreateCollectionForm(collection_form_data)
        self.assertTrue(collection_form.is_valid())

    def test_form_invalid(self):
        """Test the create collection form is invalid if required field is missing."""
        collection_form_data = {'collection_list': 'collection_list/placeholder.png',
                                'name': '',
                                'description': "It's missing!"}
        collection_form = CreateCollectionForm(collection_form_data)
        self.assertFalse(collection_form.is_valid())
        collection_form_data = {'collection_list': 'collection_list/placeholder.png',
                                'name': 'Missing',
                                'description': ''}
        collection_form = CreateCollectionForm(collection_form_data)
        self.assertFalse(collection_form.is_valid())


class CollectionEditViewTest(TestCase):
    """Test collection edit view."""

    def test_unauthenticated_access(self):
        """Unauthenticated user will be redirected to login page."""
        collection = create_collection("Easy")
        edit_url = reverse("edit_collection", kwargs={"collection_id": collection.id})
        response = self.client.get(edit_url, follow=True)
        self.assertRedirects(response, f"/accounts/login/?next={edit_url}")

    def test_not_collection_owner(self):
        """User who is not the collection owner cannot edit collection."""
        user_1 = User.objects.create_user(username="One", password="Onetest")
        user_2 = User.objects.create_user(username="Two", password="Twotest")
        collection = create_collection("Easy", user=user_1)
        edit_url = reverse("edit_collection", args=[collection.id])
        view_url = reverse("collection", args=[collection.id])
        self.client.login(username=user_2.username, password="Twotest")
        response = self.client.get(edit_url, follow=True)
        self.assertRedirects(response, view_url)

    def test_collection_owner(self):
        """User who is the collection owner can edit just fine."""
        user = User.objects.create_user(username="One", password="One pass")
        collection = create_collection("Easy", user=user)
        edit_url = reverse("edit_collection", args=[collection.id])
        self.client.login(username=user.username, password="One pass")
        response = self.client.get(edit_url, follow=True)
        self.assertTemplateUsed(response, "beatmap_collections/edit_collection.html")


class AddBeatmapViewTest(TestCase):
    """Test adding beatmap to a collection."""

    def setUp(self) -> None:
        self.owner_password = "Test"
        self.owner = User.objects.create_user(username="Test", password=self.owner_password)
        self.not_owner_password = "Test_2"
        self.not_owner = User.objects.create_user(username="Test_2", password=self.not_owner_password)
        # Beatmap model contains default value.
        self.beatmap = Beatmap.objects.create()
        self.collection = create_collection("Test", self.owner)

    def test_unauthenticated(self):
        """Unauthenticated user cannot add beatmap."""

        add_beatmap_url = reverse("add_beatmap", args=[self.collection.id])
        response = self.client.get(add_beatmap_url, follow=True)
        self.assertRedirects(response, f"/accounts/login/?next={add_beatmap_url}")

    @skip("We will test after add beatmap approval system.")
    def test_not_owner(self):
        """User cannot add a beatmap if they are not the owner."""
        add_beatmap_url = reverse("add_beatmap", args=[self.collection.id])
        collection_url = reverse("collection", args=[self.collection.id])
        self.client.login(username=self.not_owner.username, password=self.not_owner_password)
        response = self.client.get(add_beatmap_url, follow=True)
        self.assertRedirects(response, collection_url)


class CollectionListingViewTest(TestCase):
    """Test collection listing on the homepage."""

    def test_with_one_collection(self):
        """Test with one collection.

        It should display collection name.
        """

        collection_1 = create_collection("Easy")
        response = self.client.get(reverse("home"))
        self.assertContains(response, collection_1.name)

    def test_with_two_collections(self):
        """Test with two collection.

        It should contain both collections' name.
        """
        collection_1 = create_collection("Easy")
        collection_2 = create_collection("Hard")
        response = self.client.get(reverse("home"))
        self.assertContains(response, collection_1.name)
        self.assertContains(response, collection_2.name)


class CollectionModelTest(TestCase):
    """Test methods in collection model."""

    def test_optimize_image(self):
        """Test image optimization with image larger than specific size."""

        collection_image_mock = MagicMock(return_value=None)
        collection_image_mock.width = 1921
        collection_image_mock.height = 1000
        models.Model.save = MagicMock()
        collection_image_mock.thumbnail = MagicMock()
        Image.open = MagicMock(return_value=collection_image_mock)
        collection = Collection.objects.create(name="Mock")
        collection.collection_list = collection_image_mock
        collection.save()
        width, height = collection_image_mock.thumbnail.call_args[0][0]
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)


@skip("I don't know why this test cannot run in GitHub Actions")
class BeatmapImportTest(TestCase):
    """Test beatmap import function from osu! API"""

    @patch('sys.stdout', new_callable=io.StringIO)
    def import_beatmap(self, beatmap_id, expected_output, mock_stdout):
        """Get value that console print"""
        beatmap = create_beatmap(beatmap_id)
        self.assertEqual(mock_stdout.getvalue(), expected_output)
        return beatmap

    def test_import_osu_graveyard_beatmap(self):
        """Test import osu! beatmap with graveyard status"""
        osu_graveyard_beatmap = self.import_beatmap(3238306, "")
        self.assertNotEqual(osu_graveyard_beatmap, None)

    def test_import_osu_pending_beatmap(self):
        """Test import osu! beatmap with pending status"""
        osu_pending_beatmap = self.import_beatmap(3293365, "")
        self.assertNotEqual(osu_pending_beatmap, None)

    def test_import_osu_loved_beatmap(self):
        """Test import osu! beatmap with loved status"""
        osu_loved_beatmap = self.import_beatmap(1572866, "")
        self.assertNotEqual(osu_loved_beatmap, None)

    def test_import_osu_ranked_beatmap(self):
        """Test import osu! beatmap with ranked status"""
        osu_ranked_beatmap = self.import_beatmap(3157181, "")
        self.assertNotEqual(osu_ranked_beatmap, None)

    def test_import_taiko_graveyard_beatmap(self):
        """Test import taiko beatmap with graveyard status"""
        taiko_graveyard_beatmap = self.import_beatmap(3194148, "")
        self.assertNotEqual(taiko_graveyard_beatmap, None)

    def test_import_taiko_pending_beatmap(self):
        """Test import taiko beatmap with pending status"""
        taiko_pending_beatmap = self.import_beatmap(3294208, "")
        self.assertNotEqual(taiko_pending_beatmap, None)

    def test_import_taiko_loved_beatmap(self):
        """Test import taiko beatmap with loved status"""
        taiko_loved_beatmap = self.import_beatmap(2231614, "")
        self.assertNotEqual(taiko_loved_beatmap, None)

    def test_import_taiko_ranked_beatmap(self):
        """Test import taiko beatmap with ranked status"""
        taiko_ranked_beatmap = self.import_beatmap(3204946, "")
        self.assertNotEqual(taiko_ranked_beatmap, None)

    def test_import_catch_graveyard_beatmap(self):
        """Test import catch beatmap with graveyard status"""
        catch_graveyard_beatmap = self.import_beatmap(3248762, "")
        self.assertNotEqual(catch_graveyard_beatmap, None)

    def test_import_catch_pending_beatmap(self):
        """Test import catch beatmap with pending status"""
        catch_pending_beatmap = self.import_beatmap(3293380, "")
        self.assertNotEqual(catch_pending_beatmap, None)

    def test_import_catch_loved_beatmap(self):
        """Test import catch beatmap with loved status"""
        catch_loved_beatmap = self.import_beatmap(801716, "")
        self.assertNotEqual(catch_loved_beatmap, None)

    def test_import_catch_ranked_beatmap(self):
        """Test import catch beatmap with ranked status"""
        catch_ranked_beatmap = self.import_beatmap(3083866, "")
        self.assertNotEqual(catch_ranked_beatmap, None)

    def test_import_mania_graveyard_beatmap(self):
        """Test import mania beatmap with graveyard status"""
        mania_graveyard_beatmap = self.import_beatmap(3060329, "")
        self.assertNotEqual(mania_graveyard_beatmap, None)

    def test_import_mania_pending_beatmap(self):
        """Test import mania beatmap with pending status"""
        mania_pending_beatmap = self.import_beatmap(3294229, "")
        self.assertNotEqual(mania_pending_beatmap, None)

    def test_import_mania_loved_beatmap(self):
        """Test import mania beatmap with loved status"""
        mania_loved_beatmap = self.import_beatmap(883028, "")
        self.assertNotEqual(mania_loved_beatmap, None)

    def test_import_mania_ranked_beatmap(self):
        """Test import mania beatmap with ranked status"""
        mania_ranked_beatmap = self.import_beatmap(3143428, "")
        self.assertNotEqual(mania_ranked_beatmap, None)


class TemplateTagsFunctionTest(TestCase):
    """Test template tags functions."""

    def test_convert_progress_bar(self):
        """Test convert integer to value that use in progress bar."""
        self.assertEqual(convert_progress_bar(7), 70)
        self.assertEqual(convert_progress_bar(0), 0)
        self.assertEqual(convert_progress_bar(10), 100)
        self.assertEqual(convert_progress_bar(2.25), 22.5)
        self.assertEqual(convert_progress_bar(10.5), 100)
        self.assertEqual(convert_progress_bar(0.5), 5)

    def test_convert_star_rating(self):
        """Test convert star rating function."""
        self.assertEqual(convert_star_rating(7.5678), 7.57)
        self.assertEqual(convert_star_rating(17.0000), 17.00)
        self.assertEqual(convert_star_rating(0.0000), 0.00)
        self.assertEqual(convert_star_rating(2.5421), 2.54)
        self.assertEqual(convert_star_rating("I dunno"), None)

    @skip("We are thinking on this test that is it important or not.")
    def test_count_beatmaps(self):
        """Test count beatmaps function."""
        user = User.objects.create(username="SurinBoyInwZaa", id=85)
        dummy_collection = Collection.objects.create(name="Prayuth the collection",
                                                     description="Song to kick Prayuth out of the world.",
                                                     author=user)
        self.assertEqual(count_beatmaps(dummy_collection), "0 beatmap")
        beatmap_entry_1 = BeatmapEntry.objects.create(beatmap=create_beatmap(75), collection=dummy_collection, author=user)
        beatmap_entry_1.save()
        self.assertEqual(count_beatmaps(dummy_collection), "1 beatmap")
        beatmap_entry_2 = BeatmapEntry.objects.create(beatmap=create_beatmap(712376), collection=dummy_collection, author=user)
        beatmap_entry_2.save()
        beatmap_entry_3 = BeatmapEntry.objects.create(beatmap=create_beatmap(240093), collection=dummy_collection, author=user)
        beatmap_entry_3.save()
        self.assertEqual(count_beatmaps(dummy_collection), "3 beatmaps")

    def test_length_format(self):
        """Test convert length to display string."""
        self.assertEqual(length_format(0), "00:00")
        self.assertEqual(length_format(1), "00:01")
        self.assertEqual(length_format(60), "01:00")
        self.assertEqual(length_format(76), "01:16")
        self.assertEqual(length_format(490), "08:10")
        self.assertEqual(length_format(3600), "01:00:00")
        self.assertEqual(length_format(3720), "01:02:00")

    def test_thousand_seperator(self):
        """Test convert integer to string with thousand seperator."""
        self.assertEqual(thousand_seperator(1), "1")
        self.assertEqual(thousand_seperator(96), "96")
        self.assertEqual(thousand_seperator(752), "752")
        self.assertEqual(thousand_seperator(4125), "4,125")
        self.assertEqual(thousand_seperator(72349), "72,349")
        self.assertEqual(thousand_seperator(764823), "764,823")
        self.assertEqual(thousand_seperator(9481634), "9,481,634")
        self.assertEqual(thousand_seperator(19481634), "19,481,634")
        self.assertEqual(thousand_seperator(719481634), "719,481,634")
        self.assertEqual(thousand_seperator(2719481634), "2,719,481,634")
