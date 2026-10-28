"""Utilitaires pour les API internes en lecture seule (consommées par atelierProjet)."""
import hmac

from django.conf import settings
from django.http import JsonResponse


class InternalAPIKeyRequiredMixin:
    """Protège une vue par clé API partagée (en-tête ``X-API-Key``).

    Échoue fermé : si ``INTERNAL_API_KEY`` n'est pas configurée, tout accès est refusé.
    Les vues qui utilisent ce mixin ne doivent définir que ``get()`` — toute autre
    méthode HTTP est déjà rejetée avec 405 par ``django.views.View.dispatch``.
    """

    def dispatch(self, request, *args, **kwargs):
        provided = request.headers.get("X-API-Key", "")
        expected = settings.INTERNAL_API_KEY
        if not expected or not hmac.compare_digest(provided, expected):
            return JsonResponse({"detail": "Clé API invalide ou manquante."}, status=401)
        return super().dispatch(request, *args, **kwargs)


def parse_since_id(request):
    """Lit le paramètre ``?since_id=`` pour une récupération incrémentale, ou None."""
    raw = request.GET.get("since_id")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None
