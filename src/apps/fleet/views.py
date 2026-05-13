from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from .models import Vehicle


class FleetDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "fleet/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehicles"] = Vehicle.objects.filter(client=self.request.user)
        return ctx


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "fleet/vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.filter(client=self.request.user).order_by("license_plate")


class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = "fleet/vehicle_detail.html"
    context_object_name = "vehicle"

    def get_queryset(self):
        return Vehicle.objects.filter(client=self.request.user)
