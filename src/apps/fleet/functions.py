from typing import Any
from .models import Vehicle, MaintenanceRecord


def get_fleet_stats(user) -> dict[str, Any]:
    vehicles = Vehicle.objects.filter(client=user)
    return {
        'total': vehicles.count(),
        'interventions_recentes': (
            MaintenanceRecord.objects
            .filter(vehicle__client=user)
            .select_related('vehicle')
            .order_by('-date')[:5]
        ),
    }
