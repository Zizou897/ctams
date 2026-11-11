import time

from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .antispam import get_client_ip, is_rate_limited, make_timestamp_token
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


class GetClientIpTests(TestCase):
    """IP réelle du visiteur derrière Nginx (gunicorn voit toujours 127.0.0.1)."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_trusts_x_real_ip_when_remote_addr_is_loopback(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="203.0.113.5")

        self.assertEqual(get_client_ip(request), "203.0.113.5")

    def test_trusts_x_real_ip_when_remote_addr_is_ipv6_loopback(self):
        request = self.factory.get("/", REMOTE_ADDR="::1", HTTP_X_REAL_IP="203.0.113.5")

        self.assertEqual(get_client_ip(request), "203.0.113.5")

    def test_ignores_x_real_ip_when_remote_addr_is_not_loopback(self):
        request = self.factory.get("/", REMOTE_ADDR="198.51.100.9", HTTP_X_REAL_IP="203.0.113.5")

        self.assertEqual(get_client_ip(request), "198.51.100.9")

    def test_falls_back_to_remote_addr_when_x_real_ip_is_invalid(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="pas-une-ip")

        self.assertEqual(get_client_ip(request), "127.0.0.1")

    def test_falls_back_to_remote_addr_when_x_real_ip_is_missing(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1")

        self.assertEqual(get_client_ip(request), "127.0.0.1")


@override_settings(CACHES=_LOCMEM_CACHE)
class RateLimitPerRealIpTests(TestCase):
    """La limite de fréquence distingue les visiteurs par IP réelle (X-Real-IP),
    pas seulement par REMOTE_ADDR — toujours 127.0.0.1 derrière Nginx en prod."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.factory = RequestFactory()

    def _request_from(self, real_ip):
        return self.factory.get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP=real_ip)

    def test_two_real_ips_behind_the_same_loopback_have_separate_counters(self):
        visitor_a = self._request_from("203.0.113.5")
        visitor_b = self._request_from("203.0.113.6")

        for _ in range(5):
            self.assertFalse(is_rate_limited(visitor_a, "contact"))
        self.assertTrue(is_rate_limited(visitor_a, "contact"))

        # Un autre visiteur, derrière le même Nginx, n'est pas pénalisé.
        self.assertFalse(is_rate_limited(visitor_b, "contact"))
