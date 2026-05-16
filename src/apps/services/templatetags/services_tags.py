from django import template

register = template.Library()


@register.filter
def format_price(value) -> str:
    if value is None:
        return 'Sur devis'
    return f"{int(value):,} FCFA".replace(',', ' ')


@register.filter
def price_range(service) -> str:
    if service.price_on_quote:
        return 'Sur devis'
    if service.price_light_min and service.price_light_max:
        return f"{service.price_light_min:,} – {service.price_light_max:,} FCFA".replace(',', ' ')
    if service.price_light_min:
        return f"À partir de {service.price_light_min:,} FCFA".replace(',', ' ')
    return 'Sur devis'
