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
    vehicle_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Nombre de véhicules")
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


# ── Devis ─────────────────────────────────────────────────────────────────────

class DevisStatus(models.TextChoices):
    DRAFT    = "brouillon", "Brouillon"
    SENT     = "envoye",    "Envoyé"
    ACCEPTED = "accepte",   "Accepté"
    REJECTED = "refuse",    "Refusé"
    EXPIRED  = "expire",    "Expiré"


class Devis(models.Model):
    reference = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name="Référence"
    )
    quote_request = models.ForeignKey(
        QuoteRequest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="devis", verbose_name="Demande source"
    )

    # Informations client
    company_name  = models.CharField(max_length=200, verbose_name="Entreprise")
    contact_name  = models.CharField(max_length=150, verbose_name="Contact")
    email         = models.EmailField(verbose_name="Email")
    phone         = models.CharField(max_length=20, verbose_name="Téléphone")
    vehicle_count = models.PositiveSmallIntegerField(default=1, verbose_name="Nombre de véhicules")

    # Statut & validité
    status      = models.CharField(
        max_length=20, choices=DevisStatus.choices,
        default=DevisStatus.DRAFT, verbose_name="Statut"
    )
    valid_until = models.DateField(null=True, blank=True, verbose_name="Valide jusqu'au")

    # Conditions financières
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=18.00, verbose_name="TVA (%)"
    )

    # Texte libre
    notes = models.TextField(blank=True, verbose_name="Notes internes")
    terms = models.TextField(blank=True, verbose_name="Conditions de paiement")

    # Méta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="devis_crees", verbose_name="Créé par"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

    def __str__(self):
        return f"{self.reference} — {self.company_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            year = timezone.now().year
            last = (
                Devis.objects
                .filter(reference__startswith=f"CTAMS-{year}-")
                .order_by("-reference")
                .first()
            )
            if last:
                try:
                    last_num = int(last.reference.split("-")[-1])
                except (ValueError, IndexError):
                    last_num = 0
                next_num = last_num + 1
            else:
                next_num = 1
            self.reference = f"CTAMS-{year}-{next_num:04d}"
        super().save(*args, **kwargs)

    # ── Calculs ──────────────────────────────────────────────────────────────

    def get_subtotal(self):
        return sum(line.get_total() for line in self.lines.all())

    def get_tax_amount(self):
        from decimal import Decimal
        return self.get_subtotal() * (self.tax_rate / Decimal("100"))

    def get_total(self):
        return self.get_subtotal() + self.get_tax_amount()


class DevisLine(models.Model):
    devis       = models.ForeignKey(
        Devis, on_delete=models.CASCADE, related_name="lines", verbose_name="Devis"
    )
    description = models.CharField(max_length=300, verbose_name="Description")
    quantity    = models.DecimalField(
        max_digits=10, decimal_places=2, default=1, verbose_name="Quantité"
    )
    unit        = models.CharField(max_length=30, default="forfait", verbose_name="Unité")
    unit_price  = models.DecimalField(
        max_digits=12, decimal_places=0, verbose_name="Prix unitaire (FCFA)"
    )

    class Meta:
        verbose_name = "Ligne de devis"
        verbose_name_plural = "Lignes de devis"

    def __str__(self):
        return f"{self.description} × {self.quantity}"

    def get_total(self):
        return self.quantity * self.unit_price
