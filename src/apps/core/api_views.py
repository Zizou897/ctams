"""API interne en lecture seule — messages de contact (consommée par atelierProjet)."""
from django.http import JsonResponse
from django.views import View

from .api_utils import InternalAPIKeyRequiredMixin, parse_since_id
from .models import ContactMessage

MAX_RESULTS = 500


class ContactMessageListAPIView(InternalAPIKeyRequiredMixin, View):
    """Liste des messages de contact, triés par id croissant."""

    def get(self, request, *args, **kwargs):
        qs = ContactMessage.objects.order_by("id")
        since_id = parse_since_id(request)
        if since_id is not None:
            qs = qs.filter(id__gt=since_id)
        results = [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "phone": m.phone,
                "message": m.message,
                "is_read": m.is_read,
                "created_at": m.created_at,
            }
            for m in qs[:MAX_RESULTS]
        ]
        return JsonResponse({"results": results}, json_dumps_params={"ensure_ascii": False})
