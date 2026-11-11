"""Protection anti-spam des formulaires publics : honeypot, délai de remplissage
et limite de fréquence par IP. Un échec de ces contrôles ne doit jamais produire
d'erreur visible — la vue appelante répond alors comme en cas de succès, sans
rien enregistrer ni envoyer d'email (voir apps/core/views.py, apps/quotes/views.py)."""
import ipaddress
import time

from django import forms
from django.core import signing
from django.core.cache import cache

HONEYPOT_FIELD_NAME = "site_web"
TIMESTAMP_FIELD_NAME = "horodatage"

_SIGNING_SALT = "ctams.antispam.timestamp"
MIN_FILL_SECONDS = 3
MAX_FORM_AGE_SECONDS = 3600
_LOOPBACK_ADDRESSES = {"127.0.0.1", "::1"}


def get_client_ip(request):
    """IP réelle du visiteur, derrière Nginx (gunicorn voit toujours 127.0.0.1).

    Si la connexion vient de la machine locale (Nginx), on fait confiance à
    ``X-Real-IP`` (transmis par Nginx) après validation de son format ; sinon
    — connexion directe, non locale — on ne lui fait jamais confiance, pour
    éviter qu'un visiteur l'usurpe afin de contourner la limite de fréquence.
    """
    remote_addr = request.META.get("REMOTE_ADDR") or ""
    if remote_addr not in _LOOPBACK_ADDRESSES:
        return remote_addr

    real_ip = (request.META.get("HTTP_X_REAL_IP") or "").strip()
    try:
        ipaddress.ip_address(real_ip)
    except ValueError:
        return remote_addr
    return real_ip


def make_timestamp_token(at=None):
    """Jeton signé portant l'horodatage d'affichage du formulaire (champ caché).

    ``at`` (epoch en secondes) permet aux tests de simuler un formulaire affiché
    il y a N secondes, sans dépendre d'un vrai délai d'attente.
    """
    issued_at = int(at if at is not None else time.time())
    return signing.dumps(issued_at, salt=_SIGNING_SALT)


def _timestamp_token_is_valid(token):
    if not token:
        return False
    try:
        issued_at = signing.loads(token, salt=_SIGNING_SALT, max_age=MAX_FORM_AGE_SECONDS)
    except signing.BadSignature:
        return False
    return (time.time() - issued_at) >= MIN_FILL_SECONDS


class AntiSpamFormMixin(forms.Form):
    """Ajoute un honeypot invisible et un jeton horodaté à un formulaire public.

    ``is_bot()`` doit être appelé par la vue, indépendamment de ``is_valid()`` :
    un robot qui remplit le honeypot ou soumet trop vite doit recevoir la même
    réponse qu'un envoi réussi, sans jamais voir d'erreur de validation.
    """

    site_web = forms.CharField(required=False, widget=forms.TextInput())
    horodatage = forms.CharField(required=False, widget=forms.HiddenInput())

    def is_bot(self):
        if not self.is_bound:
            return False
        if (self.data.get(HONEYPOT_FIELD_NAME) or "").strip():
            return True
        return not _timestamp_token_is_valid(self.data.get(TIMESTAMP_FIELD_NAME))


def is_rate_limited(request, form_key, limit=5, period_seconds=3600):
    """Incrémente et vérifie le nombre de soumissions par IP pour ce formulaire.

    Retourne True si la limite est dépassée : la vue doit alors répondre comme
    en cas de succès, sans rien enregistrer ni envoyer d'email.
    """
    ip = get_client_ip(request) or "inconnu"
    cache_key = f"antispam:{form_key}:{ip}"
    try:
        count = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=period_seconds)
        count = 1
    return count > limit
