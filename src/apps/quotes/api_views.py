"""API interne en lecture seule — devis et demandes de devis (consommée par atelierProjet)."""
from django.http import JsonResponse
from django.views import View

from apps.core.api_utils import InternalAPIKeyRequiredMixin, parse_since_id

from .models import Devis, QuoteRequest

MAX_RESULTS = 500


class QuoteRequestListAPIView(InternalAPIKeyRequiredMixin, View):
    """Liste des demandes de devis, triées par id croissant."""

    def get(self, request, *args, **kwargs):
        qs = QuoteRequest.objects.order_by("id")
        since_id = parse_since_id(request)
        if since_id is not None:
            qs = qs.filter(id__gt=since_id)
        results = [
            {
                "id": q.id,
                "company_name": q.company_name,
                "contact_name": q.contact_name,
                "email": q.email,
                "phone": q.phone,
                "vehicle_count": q.vehicle_count,
                "service_type": q.service_type,
                "message": q.message,
                "is_processed": q.is_processed,
                "created_at": q.created_at,
            }
            for q in qs[:MAX_RESULTS]
        ]
        return JsonResponse({"results": results}, json_dumps_params={"ensure_ascii": False})


class DevisListAPIView(InternalAPIKeyRequiredMixin, View):
    """Liste des devis formels, lignes incluses. Les notes internes ne sont pas exposées."""

    def get(self, request, *args, **kwargs):
        qs = Devis.objects.prefetch_related("lines").order_by("id")
        since_id = parse_since_id(request)
        if since_id is not None:
            qs = qs.filter(id__gt=since_id)
        results = [
            {
                "id": d.id,
                "reference": d.reference,
                "quote_request_id": d.quote_request_id,
                "company_name": d.company_name,
                "contact_name": d.contact_name,
                "email": d.email,
                "phone": d.phone,
                "vehicle_count": d.vehicle_count,
                "status": d.status,
                "valid_until": d.valid_until,
                "tax_rate": d.tax_rate,
                "terms": d.terms,
                "created_at": d.created_at,
                "updated_at": d.updated_at,
                "subtotal": d.get_subtotal(),
                "tax_amount": d.get_tax_amount(),
                "total": d.get_total(),
                "lines": [
                    {
                        "id": line.id,
                        "description": line.description,
                        "quantity": line.quantity,
                        "unit": line.unit,
                        "unit_price": line.unit_price,
                        "total": line.get_total(),
                    }
                    for line in d.lines.all()
                ],
            }
            for d in qs[:MAX_RESULTS]
        ]
        return JsonResponse({"results": results}, json_dumps_params={"ensure_ascii": False})
