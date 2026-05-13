from django.db import models


class ServiceType(models.TextChoices):
    FLEET_CONTRACT = "contrat_flotte", "Contrat d'entretien de flotte"
    REPAIR = "reparation", "Réparation / Dépannage"
    WASHING = "lavage", "Lavage & Nettoyage"
    PARTS = "pieces", "Vente de pièces"
    OTHER = "autre", "Autre"


class QuoteRequest(models.Model):
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    contact_name = models.CharField(max_length=150, verbose_name="Nom du contact")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    vehicle_count = models.PositiveSmallIntegerField(verbose_name="Nombre de véhicules")
    service_type = models.CharField(max_length=30, choices=ServiceType.choices, verbose_name="Service souhaité")
    message = models.TextField(blank=True, verbose_name="Message complémentaire")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, verbose_name="Traité")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"

    def __str__(self):
        return f"{self.company_name} — {self.created_at:%d/%m/%Y}"
