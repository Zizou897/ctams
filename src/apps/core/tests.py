from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


class ContactMessageListAPIViewTests(TestCase):
    def setUp(self):
        self.url = reverse("internal_api:contact-messages")

    @override_settings(INTERNAL_API_KEY="test-shared-key")
    def test_requires_internal_api_key(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    @override_settings(INTERNAL_API_KEY="test-shared-key")
    def test_returns_contact_messages_for_authenticated_consumer(self):
        message = ContactMessage.objects.create(
            name="Awa Koné",
            email="awa@example.ci",
            phone="0700000000",
            message="Je souhaite être rappelée pour un contrat de flotte.",
        )

        response = self.client.get(
            self.url,
            HTTP_X_API_KEY="test-shared-key",
        )

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        created_at = results[0].pop("created_at")
        self.assertEqual(results[0], {
            "id": message.id,
            "name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "message": "Je souhaite être rappelée pour un contrat de flotte.",
            "is_read": False,
        })
        self.assertEqual(created_at[:19], message.created_at.isoformat()[:19])
