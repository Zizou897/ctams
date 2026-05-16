from .models import Service, ServiceCategory


def get_active_services():
    return (
        Service.objects
        .filter(is_active=True)
        .order_by('category', 'order', 'name')
    )


def get_services_by_category() -> dict:
    services = get_active_services()
    grouped: dict[str, list] = {}
    for service in services:
        label = service.get_category_display()
        grouped.setdefault(label, []).append(service)
    return grouped
