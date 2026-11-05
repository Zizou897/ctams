from django.test import TestCase, override_settings
from django.urls import reverse

from .models import QuoteRequest


class QuoteRequestListAPIViewTests(TestCase):
    def setUp(self):
        self.url = reverse("internal_api:quote-requests")

    @override_settings(INTERNAL_API_KEY="test-shared-key")
    def test_requires_internal_api_key(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    @override_settings(INTERNAL_API_KEY="test-shared-key")
    def test_returns_submitted_quote_requests_for_authenticated_consumer(self):
        quote = QuoteRequest.objects.create(
            company_name="Entreprise Démo",
            contact_name="Awa Koné",
            email="awa@example.ci",
            phone="0700000000",
            vehicle_count=12,
            service_type="contrat_flotte",
            message="Entretien de flotte",
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
            "id": quote.id,
            "company_name": "Entreprise Démo",
            "contact_name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "vehicle_count": 12,
            "service_type": "contrat_flotte",
            "service_type_label": "Contrat d'entretien de flotte",
            "message": "Entretien de flotte",
            "is_processed": False,
        })
        self.assertEqual(
            created_at[:19],
            quote.created_at.isoformat()[:19],
        )
