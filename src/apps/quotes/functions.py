from .models import QuoteRequest


def get_pending_quotes():
    return QuoteRequest.objects.filter(is_processed=False).order_by('-created_at')
