"""
Tests for views in users app.
"""
from django.test import TestCase
from django.urls import reverse
from beatmap_collections.tests import prepare_collections
from .models import *


class SettingsViewTest(TestCase):
    """Tests for the settings view."""

    def setUp(self):
        """Create a dummy user and a constant containing the settings url."""
        self.user = User.objects.create_user(username="Dummy", password="QuakeWorldForever")
        self.url = reverse("settings")

    def test_settings_view_not_logged_in(self):
        """If the user is not logged in, redirect them to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/settings/")

    def test_settings_view_display(self):
        """Test if the settings view displays the settings template when it receives a get request."""
        self.client.login(username="Dummy", password="QuakeWorldForever")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/settings.html')

    def test_settings_view_modify(self):
        """Test if the settings view redirects back to itself, provided that all required fields are
        filled out."""
        # Create a post data. For context, only the username field is required.
        user_update_data = {"username": "DummyV2"}
        self.client.login(username="Dummy", password="QuakeWorldForever")
        response = self.client.post(self.url, user_update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)


class ProfileViewTests(TestCase):
    """Tests for the profile view."""

    # These properties will be initialized in setUpTestData.
    user = None
    collections = None

    @classmethod
    def setUpTestData(cls):
        """Create a dummy user to test with."""
        cls.user = User.objects.create_user(username="Dummy", password="QuakeWorldForever")
        cls.collections = prepare_collections(amount=20, user=cls.user)
        cls.profile_url = reverse("profile", args=[cls.user.id])

    def test_profile_view_valid_user(self):
        """The profile view should return the requested user's profile page if the user id is valid."""
        # Try to get the user with an id of 1, the dummy user.
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_invalid_user(self):
        """The profile view should return a 404 if the specified user id is invalid."""
        # Try to get the user with an id of 2, a nonexistent user.
        url = reverse("profile", args=[2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_paginated(self):
        """Collections should be paginated."""
        response = self.client.get(self.profile_url)
        self.assertQuerysetEqual(response.context['collections'], self.collections[:10])
        response = self.client.get(self.profile_url, {'page': 2})
        self.assertQuerysetEqual(response.context['collections'], self.collections[10:])

    def test_paginated_not_integer(self):
        """If the page number is not an integer, it uses the first page."""
        response = self.client.get(self.profile_url, {'page': 'ninja'})
        self.assertQuerysetEqual(response.context['collections'], self.collections[:10])

    def test_paginated_exceed_maximum(self):
        """If the page number exceeds the maximum, it uses the last page."""
        response = self.client.get(self.profile_url, {'page': 999})
        self.assertQuerysetEqual(response.context['collections'], self.collections[10:])
