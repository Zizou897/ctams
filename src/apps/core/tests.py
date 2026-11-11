import time

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .antispam import make_timestamp_token
from .models import ContactMessage

_LOCMEM_CACHE = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


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


class HomeViewTests(TestCase):
    @override_settings(CTAMS_PARTNERS_API_URL="https://atelierprojet.example/api/partners/")
    def test_homepage_exposes_configured_partners_api_url(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'data-api-url="https://atelierprojet.example/api/partners/"',
        )

    @override_settings(CTAMS_PARTNERS_API_URL="")
    def test_homepage_renders_when_partners_api_url_is_not_configured(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="partners-status"')


@override_settings(CACHES=_LOCMEM_CACHE)
class ContactFormAntiSpamTests(TestCase):
    """Protection anti-spam du formulaire de contact : honeypot, délai de
    remplissage, limite de fréquence par IP et refus des liens/HTML."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.url = reverse("core:contact")
        self.success_url = reverse("core:contact") + "?sent=1"
        self.valid_data = {
            "name": "Awa Koné",
            "email": "awa@example.ci",
            "phone": "0700000000",
            "message": "Je souhaite un devis pour l'entretien de ma flotte.",
            "site_web": "",
            "horodatage": make_timestamp_token(at=time.time() - 10),
        }

    def test_valid_human_submission_is_saved_and_emailed(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_honeypot_filled_is_silently_ignored(self):
        data = {**self.valid_data, "site_web": "http://spam.example"}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_submission_too_fast_is_silently_ignored(self):
        data = {**self.valid_data, "horodatage": make_timestamp_token()}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_timestamp_token_is_silently_ignored(self):
        data = {**self.valid_data, "horodatage": ""}
        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_rate_limit_exceeded_is_silently_ignored(self):
        for _ in range(5):
            self.client.post(self.url, self.valid_data)
        self.assertEqual(ContactMessage.objects.count(), 5)

        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(ContactMessage.objects.count(), 5)
        self.assertEqual(len(mail.outbox), 5)

    def test_link_in_message_is_rejected_with_a_clear_error(self):
        data = {**self.valid_data, "message": "Voir http://spam.example pour plus d'infos"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, "lien")

    def test_html_tag_in_name_is_rejected_with_a_clear_error(self):
        data = {**self.valid_data, "name": "<b>Awa</b>"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_phone_over_20_characters_does_not_crash(self):
        data = {**self.valid_data, "phone": "0" * 25}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
