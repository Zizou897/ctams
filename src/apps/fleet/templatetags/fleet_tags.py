from django import template

register = template.Library()


@register.filter
def vehicle_type_badge(vehicle_type: str) -> str:
    classes = {
        'vl': 'bg-blue-100 text-blue-800',
        'vu': 'bg-purple-100 text-purple-800',
        'pl': 'bg-orange-100 text-orange-800',
        'engin': 'bg-yellow-100 text-yellow-800',
    }
    return classes.get(vehicle_type, 'bg-gray-100 text-gray-600')


@register.filter
def format_mileage(value) -> str:
    if value is None:
        return '—'
    return f"{int(value):,} km".replace(',', ' ')
