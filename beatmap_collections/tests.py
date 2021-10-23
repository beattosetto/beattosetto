from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from .forms import *


class CreateCollectionViewTests(TestCase):
    """Tests for the create_collection_page view."""

    def test_login_user_only(self):
        """If the user is not logged in they can't access the page."""
        user = User.objects.create(username="GordonFreeman")
        user.set_password('12345')
        user.save()

        # Test logged in.
        self.client.login(username='GordonFreeman', password='12345')
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('beatmap_collections/create_collection.html')
        # Test logged out.
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/login/?next=/new/')


class CreateCollectionFormTest(TestCase):
    """Tests for the create collection form."""

    def test_form_not_valid_missing_field(self):
        """Test the collection """

        user = User.objects.create(username="Surinboy")
        user.set_password('PomPenDekDee')
        user.save()

        collection_form_data = {'collection_list': '',
                                'name': 'Test',
                                'description': 'This is test'}
        collection_form = CreateCollectionForm(collection_form_data)

        self.assertFalse(collection_form.is_valid())
