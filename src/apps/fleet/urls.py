from django.urls import path
from . import views

app_name = "fleet"

urlpatterns = [
    path("", views.FleetDashboardView.as_view(), name="dashboard"),
    path("vehicules/", views.VehicleListView.as_view(), name="vehicle-list"),
    path("vehicules/<int:pk>/", views.VehicleDetailView.as_view(), name="vehicle-detail"),
]
