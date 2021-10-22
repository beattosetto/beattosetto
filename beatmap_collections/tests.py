from django.test import TestCase
from .models import *


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
        self.assertTemplateUsed('beatmap_collections/collection.html')
        # Test logged out.
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, '/login/?next=/new/')


class SaveViewTest(TestCase):
    """Tests for the save_collection view."""

    def test_collection_creation(self):
        """Test the beatmap collection creation system."""
        user = User.objects.create(username="GordonFreeman")
        user.set_password('12345')
        user.save()

        self.client.post('/save/', {"inputTitle": "Nice Collection",
                                    "inputDescription": "This is a very good collection."})
        self.client.post('/save/', {"inputTitle": "Very Nice Collection",
                                    "inputDescription": "This is a very very good collection."})
        collection_first = Collection.objects.all()[0]
        collection_second = Collection.objects.all()[1]
        self.assertEqual(collection_first.name, "Nice Collection")
        self.assertEqual(collection_first.description, "This is a very good collection.")
        self.assertEqual(collection_second.name, "Very Nice Collection")
        self.assertEqual(collection_second.description, "This is a very very good collection.")
