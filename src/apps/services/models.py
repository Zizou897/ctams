from django.db import models
from django.urls import reverse


class ServiceCategory(models.TextChoices):
    MAINTENANCE = "maintenance", "Entretien courant"
    BRAKES = "freinage", "Freinage"
    SUSPENSION = "suspension", "Suspension"
    ELECTRICAL = "electricite", "Électricité / Électronique"
    BODYWORK = "tolerie", "Tôlerie & Peinture"
    ENGINE = "motorisation", "Motorisation"
    TIRES = "pneumatiques", "Pneumatiques"
    FLEET = "forfaits", "Forfaits flotte"
    WASHING = "lavage", "Lavage & Nettoyage"


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du service")
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=ServiceCategory.choices, verbose_name="Catégorie")
    description = models.TextField(verbose_name="Description")
    price_light_min = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prix min VL (FCFA)")
    price_light_max = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prix max VL (FCFA)")
    price_heavy_min = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prix min PL (FCFA)")
    price_heavy_max = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prix max PL (FCFA)")
    price_on_quote = models.BooleanField(default=False, verbose_name="Sur devis")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category", "order", "name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("services:detail", kwargs={"slug": self.slug})

    @property
    def price_display_light(self):
        if self.price_on_quote:
            return "Sur devis"
        if self.price_light_min and self.price_light_max:
            return f"{self.price_light_min:,} – {self.price_light_max:,} FCFA"
        if self.price_light_min:
            return f"À partir de {self.price_light_min:,} FCFA"
        return "Sur devis"
