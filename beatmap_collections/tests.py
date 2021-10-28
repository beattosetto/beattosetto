from unittest.mock import MagicMock

from django.test import TestCase
from django.http import HttpRequest
from django.urls import reverse

from .models import *
from .forms import *
from django.db import models


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
