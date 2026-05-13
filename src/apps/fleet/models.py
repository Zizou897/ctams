from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class VehicleType(models.TextChoices):
    LIGHT = "vl", "Véhicule léger"
    UTILITY = "vu", "Utilitaire"
    HEAVY = "pl", "Poids lourd"
    MACHINERY = "engin", "Engin"


class Vehicle(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    license_plate = models.CharField(max_length=20, verbose_name="Immatriculation")
    brand = models.CharField(max_length=100, verbose_name="Marque")
    model = models.CharField(max_length=100, verbose_name="Modèle")
    year = models.PositiveSmallIntegerField(verbose_name="Année")
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, verbose_name="Type")
    mileage = models.PositiveIntegerField(default=0, verbose_name="Kilométrage actuel")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["license_plate"]
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"

    def __str__(self):
        return f"{self.license_plate} — {self.brand} {self.model}"

    def get_absolute_url(self):
        return reverse("fleet:vehicle-detail", kwargs={"pk": self.pk})


class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="records")
    date = models.DateField(verbose_name="Date d'intervention")
    description = models.TextField(verbose_name="Travaux réalisés")
    mileage_at_service = models.PositiveIntegerField(verbose_name="Kilométrage à l'intervention")
    cost = models.PositiveIntegerField(verbose_name="Coût (FCFA)")
    technician = models.CharField(max_length=100, blank=True, verbose_name="Technicien")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"

    def __str__(self):
        return f"{self.vehicle.license_plate} — {self.date:%d/%m/%Y}"
