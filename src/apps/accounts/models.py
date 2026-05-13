from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company_name = models.CharField(max_length=200, verbose_name="Entreprise")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    fleet_size = models.PositiveSmallIntegerField(default=0, verbose_name="Taille de flotte")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil client"
        verbose_name_plural = "Profils clients"

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"
