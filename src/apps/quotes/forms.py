from django import forms
from .models import QuoteRequest


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["company_name", "contact_name", "email", "phone", "vehicle_count", "service_type", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "company_name": "Nom de votre entreprise *",
            "contact_name": "Votre nom *",
            "email": "Email *",
            "phone": "Téléphone *",
            "vehicle_count": "Nombre de véhicules *",
            "service_type": "Service souhaité *",
            "message": "Précisions (facultatif)",
        }
