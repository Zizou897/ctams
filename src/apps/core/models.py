from django.db import models


class Convention(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish    = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ContactMessage(models.Model):
    name      = models.CharField(max_length=150, verbose_name="Nom")
    email     = models.EmailField(verbose_name="Email")
    phone     = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    message   = models.TextField(verbose_name="Message")
    is_read   = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.name} — {self.created_at:%d/%m/%Y %H:%M}"
