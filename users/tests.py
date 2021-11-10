"""
Tests for views in users app.
"""
from django.test import TestCase
from django.urls import reverse
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

    def setUp(self):
        """Create a dummy user to test with."""
        self.user = User.objects.create_user(username="Dummy", password="QuakeWorldForever")

    def test_profile_view_valid_user(self):
        """The profile view should return the requested user's profile page if the user id is valid."""
        # Try to get the user with an id of 1, the dummy user.
        url = reverse("profile", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_invalid_user(self):
        """The profile view should return a 404 if the specified user id is invalid."""
        # Try to get the user with an id of 2, a nonexistent user.
        url = reverse("profile", args=[2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
