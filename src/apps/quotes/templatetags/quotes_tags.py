from django import template

register = template.Library()


@register.filter
def status_label(is_processed: bool) -> str:
    return 'Traité' if is_processed else 'En attente'


@register.filter
def status_badge_class(is_processed: bool) -> str:
    if is_processed:
        return 'bg-green-100 text-green-800'
    return 'bg-yellow-100 text-yellow-800'
