"""
Tests for views in collection app.
"""
from datetime import timedelta
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

from .templatetags import *


def create_collection(name, user=None, days_difference=0) -> Collection:
    """Utility function for creating collection.

    Args:
        name: Collection name
        user: Test user default to None
        days_difference: Days difference from now to create collection

    The test user will have both username and password set to "test".
    """
    if user is None:
        user, _ = User.objects.get_or_create(username="test")
        user.set_password("test")
    collection = Collection.objects.create(author=user, name=name)
    collection.create_date += timedelta(days=days_difference)
    collection.save()
    return collection


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

    def test_form_valid_with_tag_missing(self):
        """Test the create collection form is valid despite the collection tags field is missing."""
        collection_form_data = {'collection_list': 'collection_list/placeholder.png',
                                'name': 'Test',
                                'description': 'This is test',
                                'tags': ''}

        collection_form = CreateCollectionForm(collection_form_data)
        self.assertTrue(collection_form.is_valid())

    def test_form_invalid(self):
        """Test the create collection form is invalid if required field is missing."""
        collection_form_data = {'collection_list': 'collection_list/placeholder.png',
                                'name': '',
                                'description': "It's missing!",
                                'tags': 'test'}
        collection_form = CreateCollectionForm(collection_form_data)
        self.assertFalse(collection_form.is_valid())
        collection_form_data = {'collection_list': 'collection_list/placeholder.png',
                                'name': 'Missing',
                                'description': '',
                                'tags': 'test'}
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


class HomeListingTest(TestCase):
    """Tests for listing on the homepage."""

    def test_up_to_four_collections(self):
        """The homepage should list upto 4 collections sorted by creation date."""
        collections = [create_collection(chr(67 + i), days_difference=-i) for i in range(10)]
        response = self.client.get(reverse("home"))
        self.assertQuerysetEqual(response.context['latest_added'], collections[:4])


class CollectionListingViewTest(TestCase):
    """Test collection listing on the homepage."""

    def test_with_one_collection(self):
        """Test with one collection.

        It should display collection name.
        """

        collection_1 = create_collection("Easy")
        response = self.client.get(reverse("listing"))
        self.assertContains(response, collection_1.name)

    def test_with_two_collections(self):
        """Test with two collection.

        It should contain both collections' name.
        """
        collection_1 = create_collection("Easy")
        collection_2 = create_collection("Hard")
        response = self.client.get(reverse("listing"))
        self.assertContains(response, collection_1.name)
        self.assertContains(response, collection_2.name)

    def test_paginated(self):
        """Test that collections are paginated.

        It should be paginated by 10.
        """
        # It is ordered by name. The chr function can make it sorted by name already.
        collections = [create_collection(chr(i)) for i in range(20)]
        response = self.client.get(reverse("listing"))
        self.assertQuerysetEqual(response.context['collections'], collections[:10])
        response = self.client.get(reverse("listing"), {'page': 2})
        self.assertQuerysetEqual(response.context['collections'], collections[10:])


class CollectionListingByTagViewTest(TestCase):
    """Test collection listing on tag view."""

    def test_with_tag(self):
        """Test crete collection with tag."""
        author = User.objects.create_user(username="test", password="test")
        collection_with_tag = Collection.objects.create(name="Test", author=author)
        collection_with_tag.tags.add("tag")
        url = reverse("collection_by_tag", args=["tag"])
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['collections'], [collection_with_tag])


class CollectionModelTest(TestCase):
    """Test methods in collection model."""

    def setUp(self):
        self.original_save_func = models.Model.save

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

        # The actual create_beatmap function interact with API.
        # That's why we don't use it in tests.
        # pylint: disable=redefined-outer-name
        def create_beatmap(beatmap_id: int):
            """Utility function for creating beatmap without interacting with API."""
            return Beatmap.objects.create(beatmap_id=beatmap_id)

        user = User.objects.create(username="SurinBoyInwZaa", id=85)
        dummy_collection = Collection.objects.create(name="Prayuth the collection",
                                                     description="Song to kick Prayuth out of the world.",
                                                     author=user)
        self.assertEqual(dummy_collection.beatmaps_count, 0)
        beatmap_entry_1 = BeatmapEntry.objects.create(beatmap=create_beatmap(75), collection=dummy_collection,
                                                      author=user, owner_approved=True)
        beatmap_entry_1.save()
        self.assertEqual(dummy_collection.beatmaps_count, 1)
        beatmap_entry_2 = BeatmapEntry.objects.create(beatmap=create_beatmap(712376), collection=dummy_collection,
                                                      author=user, owner_approved=True)
        beatmap_entry_2.save()
        beatmap_entry_3 = BeatmapEntry.objects.create(beatmap=create_beatmap(240093), collection=dummy_collection,
                                                      author=user, owner_approved=False)
        beatmap_entry_3.save()
        self.assertEqual(dummy_collection.beatmaps_count, 2)

    def tearDown(self):
        models.Model.save = self.original_save_func


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

    def test_round_up(self):
        """Test round up function."""
        self.assertEqual(round_up(0), 0)
        self.assertEqual(round_up(1), 1)
        self.assertEqual(round_up(2.5), 3)
        self.assertEqual(round_up(199.99), 200)


# @skip("Unerror occured")
class ListCollectionFromUserTest(TestCase):
    """Test for listing collection from a user."""

    def setUp(self) -> None:
        self.owner = User.objects.create_user(username="owner", password="Not important")
        self.owner_id = self.owner.id
        self.not_owner = User.objects.create_user(username="not_owner", password="Not important")

    def test_list_only_owner(self):
        """This page only lists collection from specific user."""
        collection_one = create_collection("Taiko", user=self.owner)
        collection_two = create_collection("Mono", user=self.owner)
        create_collection("Mone", user=self.not_owner)
        response = self.client.get(reverse("profile", args=[self.owner_id]))
        self.assertQuerysetEqual(
            response.context['collections'],
            [collection_one, collection_two],
            ordered=False
        )

    def test_redirect_404(self):
        """If the user does not exist, it redirects to 404."""
        response = self.client.get(reverse("profile", args=[9999]), follow=True)
        self.assertEqual(response.status_code, 404)


class BeatmapAdditionTest(TestCase):
    """Test adding beatmap."""

    @staticmethod
    def mock_create(beatmap_id: int):
        """Mock creating beatmap with specific id."""
        return Beatmap.objects.create(beatmap_id=beatmap_id)

    def add_beatmap(self, beatmap_id=12):
        """Add beatmap with placeholder id and comment."""
        collection_url = reverse("add_beatmap", args=[self.collection.id])
        self.client.post(collection_url, {
            "beatmap_id": beatmap_id,
            "comment": "Tester man"
        })

    def setUp(self) -> None:
        """Create beatmap and user."""
        self.test_user = User.objects.create_user(id=1, username="test", password="test")
        self.another_user = User.objects.create_user(id=2, username="test2", password="test2")
        self.create_beatmap_mock = patch("beatmap_collections.views.create_beatmap",
                                         side_effect=self.mock_create)
        self.create_beatmap_mock.side_effect = self.mock_create
        self.create_beatmap_mock.start()
        self.collection = Collection.objects.create(author=self.test_user)

    def tearDown(self) -> None:
        """Stop mocking create_beatmap"""
        self.create_beatmap_mock.stop()

    def test_add_beatmap_normally(self):
        """Test if the setup method is working."""
        # mock_create.side_effect = self.mock_create
        self.client.login(username="test", password="test")
        self.add_beatmap()
        self.assertEqual(self.collection.beatmaps_count, 1)
        self.assertTrue(BeatmapEntry.objects.filter(beatmap__beatmap_id=12).exists())

    def test_add_beatmap_without_comment(self):
        """User can now add beatmap without comment"""
        self.client.login(username="test", password="test")
        collection_url = reverse("add_beatmap", args=[self.collection.id])
        # Comment omitted.
        self.client.post(collection_url, {
            "beatmap_id": 12,
        })
        self.assertEqual(self.collection.beatmaps_count, 1)
        # Empty comment
        self.client.post(collection_url, {
            "beatmap_id": 12,
            "comment": ""
        })
        self.assertEqual(self.collection.beatmaps_count, 1)

    def test_add_beatmap_without_login(self):
        """User cannot add beatmap without logging in."""
        collection_url = reverse("add_beatmap", args=[self.collection.id])
        self.client.post(collection_url, {
            "beatmap_id": 12,
            "comment": "Hacker"
        }, follow=True)
        self.assertEqual(self.collection.beatmaps_count, 0)

    def test_add_existing_beatmap_entry(self):
        """User cannot add duplicate beatmap entry."""
        self.client.login(username="test", password="test")
        new_beatmap = Beatmap.objects.create(beatmap_id=12)
        new_beatmap_2 = Beatmap.objects.create(beatmap_id=13)
        self.collection.beatmapentry_set.create(
            beatmap=new_beatmap,
            author=self.test_user,
            owner_approved=True
        )
        self.add_beatmap()
        self.assertEqual(self.collection.beatmaps_count, 1)
        # Not approved now.
        self.collection.beatmapentry_set.create(
            beatmap=new_beatmap_2,
            author=self.another_user,
            owner_approved=False
        )
        self.add_beatmap(beatmap_id=13)
        self.assertEqual(self.collection.beatmaps_count, 2)


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
        beatmap_entry = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                    collection=self.collection)
        beatmap_entry.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{beatmap_entry.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertTrue(BeatmapEntry.objects.get(id=beatmap_entry.id).owner_approved)

    def test_deny_beatmap(self):
        """Test deny beatmap"""
        self.client.login(username='mrekk', password='test')
        beatmap_entry_2 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=self.collection)
        beatmap_entry_2.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{beatmap_entry_2.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertFalse(BeatmapEntry.objects.filter(id=beatmap_entry_2.id).exists())

    def test_approve_beatmap_not_owner(self):
        """Test approve beatmap but not owner"""
        self.client.login(username='pippi', password='test')
        beatmap_entry_3 = BeatmapEntry.objects.create(author=self.author, beatmap=self.beatmap,
                                                      collection=self.collection)
        beatmap_entry_3.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{beatmap_entry_3.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertFalse(BeatmapEntry.objects.get(id=beatmap_entry_3.id).owner_approved)
        beatmap_entry_4 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=self.collection,
                                                      owner_approved=True)
        beatmap_entry_4.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{beatmap_entry_4.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertTrue(BeatmapEntry.objects.get(id=beatmap_entry_4.id).owner_approved)

    def test_deny_beatmap_not_owner(self):
        """Test deny beatmap but not owner"""
        self.client.login(username='pippi', password='test')
        beatmap_entry_5 = BeatmapEntry.objects.create(author=self.author, beatmap=self.beatmap,
                                                      collection=self.collection)
        beatmap_entry_5.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{beatmap_entry_5.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertTrue(BeatmapEntry.objects.filter(id=beatmap_entry_5.id).exists())
        beatmap_entry_6 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=self.collection, owner_approved=True)
        beatmap_entry_6.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{beatmap_entry_6.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/')
        self.assertTrue(BeatmapEntry.objects.filter(id=beatmap_entry_6.id).exists())

    def test_approve_beatmap_already_approve(self):
        """Test approve beatmap that is already approved"""
        self.client.login(username='mrekk', password='test')
        beatmap_entry_7 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=self.collection, owner_approved=True)
        beatmap_entry_7.save()
        response = self.client.get(f'/collections/{self.collection.id}/approve/{beatmap_entry_7.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertTrue(BeatmapEntry.objects.get(id=beatmap_entry_7.id).owner_approved)

    def test_approve_cross_collection(self):
        """Test approving beatmap that has same id in the different collection."""
        self.client.login(username="mrekk", password="test")
        another_collection = Collection.objects.create(author=self.normal_user)
        beatmap_entry_9 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=another_collection, owner_approved=False)
        another_collection_url = reverse("approve_beatmap", args=[another_collection.id, beatmap_entry_9.id])
        response = self.client.get(another_collection_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(beatmap_entry_9.owner_approved)

    def test_deny_beatmap_already_approve(self):
        """Test deny beatmap that is already approved"""
        self.client.login(username='mrekk', password='test')
        beatmap_entry_8 = BeatmapEntry.objects.create(author=self.normal_user, beatmap=self.beatmap,
                                                      collection=self.collection,
                                                      owner_approved=True)
        beatmap_entry_8.save()
        response = self.client.get(f'/collections/{self.collection.id}/deny/{beatmap_entry_8.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/collections/{self.collection.id}/approval')
        self.assertTrue(BeatmapEntry.objects.get(id=beatmap_entry_8.id).owner_approved)
