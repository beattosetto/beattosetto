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

from .templatetags.convert_beatmap_stat import convert_beatmap_stat
from .templatetags.convert_progress_bar import convert_progress_bar
from .templatetags.convert_star_rating import convert_star_rating
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

    # @skip("We are thinking on this test that is it important or not.")
    def test_count_beatmaps(self):
        """Test count beatmaps function."""

        def create_beatmap(beatmap_id: int):
            """Create beatmap without using API.

            Calling API is irrelevant to the test.
            """
            beatmap = Beatmap.objects.create(beatmap_id=beatmap_id)

            user = User.objects.create(username="SurinBoyInwZaa", id=85)
            dummy_collection = Collection.objects.create(name="Prayuth the collection",
                                                         description="Song to kick Prayuth out of the world.",
                                                         author=user)
            self.assertEqual(dummy_collection.beatmaps_count, 0)
            beatmap_entry_1 = BeatmapEntry.objects.create(beatmap=create_beatmap(75), collection=dummy_collection,
                                                          author=user)
            beatmap_entry_1.save()
            self.assertEqual(dummy_collection.beatmaps_count, 1)
            beatmap_entry_2 = BeatmapEntry.objects.create(beatmap=create_beatmap(712376), collection=dummy_collection,
                                                          author=user)
            beatmap_entry_2.save()
            beatmap_entry_3 = BeatmapEntry.objects.create(beatmap=create_beatmap(240093), collection=dummy_collection,
                                                          author=user, owner_approved=True)
            beatmap_entry_3.save()
            self.assertEqual(dummy_collection.beatmaps_count, 1)


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

    def test_convert_beatmap_stat(self):
        """Test convert beatmap stat function."""
        self.assertEqual(convert_beatmap_stat(0), 0)
        self.assertEqual(convert_beatmap_stat(10), 10)
        self.assertEqual(convert_beatmap_stat(10.5), 10.5)
        self.assertEqual(convert_beatmap_stat(10.567), 10.6)
        self.assertEqual(convert_beatmap_stat(80.6666666), 80.7)
        self.assertEqual(convert_beatmap_stat("Why this value here"), "Why this value here")


class ListCollectionFromUserTest(TestCase):
    """Test for listing collection from a user."""
    def setUp(self) -> None:
        self.owner = User.objects.create_user(username="owner", password="Not important")
        print(self.owner)
        self.owner_id = self.owner.id
        self.not_owner = User.objects.create_user(username="not_owner", password="Not important")

    def test_list_only_owner(self):
        """This page only lists collection from specific user."""
        collections = [
            create_collection("Taiko", user=self.owner),
            create_collection("Mono", user=self.owner)
        ]
        create_collection("Mone", user=self.not_owner)
        response = self.client.get(reverse("profile_collections", args=[self.owner_id]))
        self.assertQuerysetEqual(
            response.context['collections'],
            collections,
            ordered=False
        )

    def test_redirect_404(self):
        """If the user does not exist, it redirects to 404."""
        response = self.client.get(reverse("profile_collections", args=[9999]), follow=True)
        self.assertEqual(response.status_code, 404)


class BeatmapApprovalTest(TestCase):
    """Test beatmap approval."""

    def setUp(self):
        """Create beatmap and user."""
        self.author = User.objects.create_user(username="mrekk", password="test")
        self.author.save()
        self.normal_user = User.objects.create_user(username="pippi", password="test")
        self.normal_user.save()
        self.beatmap = Beatmap.objects.create(beatmap_id=12345, title="Test Beatmap")
        self.beatmap.save()
        self.collection = Collection.objects.create(name="Test Collection", author=self.author)
        self.collection.save()

    def test_beatmap_approval_page_access_without_login(self):
        """Test who not login cannot access approval page"""
        response = self.client.get(f'/collections/{self.collection.id}/approval')
        self.assertRedirects(response, f'/accounts/login/?next=/collections/{self.collection.id}/approval')

    def test_beatmap_approval_page_access_not_owner(self):
        """Test who not owner cannot access approval page"""
        self.client.login(username='pippi', password='test')
        response = self.client.get(f'/collections/{self.collection.id}/approval')
        self.assertRedirects(response, f'/collections/{self.collection.id}/')

    def test_beatmap_approval_page_access_owner(self):
        """Test who is owner can access approval page"""
        self.client.login(username='mrekk', password='test')
        response = self.client.get(f'/collections/{self.collection.id}/approval')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'beatmap_collections/beatmap_approval.html', 'beatmap_collections/base.html')

    def test_approve_beatmap(self):
        """Test approve beatmap"""
        self.client.login(username='mrekk', password='test')
        self.beatmap_entry = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection)
        self.beatmap_entry.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{self.beatmap_entry.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertEqual(BeatmapEntry.objects.get(id=self.beatmap_entry.id).owner_approved, True)

    def test_deny_beatmap(self):
        """Test deny beatmap"""
        self.client.login(username='mrekk', password='test')
        self.beatmap_entry_2 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection)
        self.beatmap_entry_2.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{self.beatmap_entry_2.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertEqual(BeatmapEntry.objects.filter(id=self.beatmap_entry_2.id).exists(), False)

    def test_approve_beatmap_not_owner(self):
        """Test approve beatmap but not owner"""
        self.client.login(username='pippi', password='test')
        self.beatmap_entry_3 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection)
        self.beatmap_entry_3.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{self.beatmap_entry_3.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertEqual(BeatmapEntry.objects.get(id=self.beatmap_entry_3.id).owner_approved, False)
        self.beatmap_entry_4 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection, owner_approved=True)
        self.beatmap_entry_4.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{self.beatmap_entry_4.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertEqual(BeatmapEntry.objects.get(id=self.beatmap_entry_4.id).owner_approved, True)

    def test_deny_beatmap_not_owner(self):
        """Test deny beatmap but not owner"""
        self.client.login(username='pippi', password='test')
        self.beatmap_entry_5 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection)
        self.beatmap_entry_5.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{self.beatmap_entry_5.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertEqual(BeatmapEntry.objects.filter(id=self.beatmap_entry_5.id).exists(), True)
        self.beatmap_entry_6 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection, owner_approved=True)
        self.beatmap_entry_6.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{self.beatmap_entry_6.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertEqual(BeatmapEntry.objects.filter(id=self.beatmap_entry_6.id).exists(), True)

    def test_approve_beatmap_already_approve(self):
        """Test approve beatmap that is already approved"""
        self.client.login(username='mrekk', password='test')
        self.beatmap_entry_7 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection, owner_approved=True)
        self.beatmap_entry_7.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{self.beatmap_entry_7.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertEqual(BeatmapEntry.objects.get(id=self.beatmap_entry_7.id).owner_approved, True)

    def test_deny_beatmap_already_approve(self):
        """Test deny beatmap that is already approved"""
        self.client.login(username='mrekk', password='test')
        self.beatmap_entry_8 = BeatmapEntry.objects.create(beatmap=self.beatmap, collection=self.collection, owner_approved=True)
        self.beatmap_entry_8.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{self.beatmap_entry_8.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertEqual(BeatmapEntry.objects.get(id=self.beatmap_entry_8.id).owner_approved, True