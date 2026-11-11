import time

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.antispam import make_timestamp_token

from .models import QuoteRequest

_LOCMEM_CACHE = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


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


@override_settings(CACHES=_LOCMEM_CACHE)
class QuoteRequestFormAntiSpamTests(TestCase):
    """Protection anti-spam de la demande de devis : honeypot, délai de
    remplissage, limite de fréquence par IP et refus des liens/HTML."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.url = reverse("quotes:request")
        self.success_url = reverse("quotes:confirmation")
        self.valid_data = {
            "company_name": "Entreprise Démo",
            "contact_name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "vehicle_count": 12,
            "service_type": "contrat_flotte",
            "message": "Entretien de flotte",
            "site_web": "",
            "horodatage": make_timestamp_token(at=time.time() - 10),
        }

    def test_valid_human_submission_is_saved_and_emailed(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_honeypot_filled_is_silently_ignored(self):
        data = {**self.valid_data, "site_web": "http://spam.example"}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_submission_too_fast_is_silently_ignored(self):
        data = {**self.valid_data, "horodatage": make_timestamp_token()}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_timestamp_token_is_silently_ignored(self):
        data = {**self.valid_data, "horodatage": ""}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_rate_limit_exceeded_is_silently_ignored(self):
        for _ in range(5):
            self.client.post(self.url, self.valid_data)
        self.assertEqual(QuoteRequest.objects.count(), 5)

        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(QuoteRequest.objects.count(), 5)
        self.assertEqual(len(mail.outbox), 5)

    def test_link_in_message_is_rejected_with_a_clear_error(self):
        data = {**self.valid_data, "message": "Voir http://spam.example pour plus d'infos"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_html_tag_in_company_name_is_rejected_with_a_clear_error(self):
        data = {**self.valid_data, "company_name": "<b>Entreprise</b>"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuoteRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_phone_over_20_characters_does_not_crash(self):
        data = {**self.valid_data, "phone": "0" * 25}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuoteRequest.objects.count(), 0)
