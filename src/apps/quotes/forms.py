from django import forms

from apps.core.antispam import AntiSpamFormMixin
from apps.core.validators import reject_links, reject_links_html_and_newlines

from .models import QuoteRequest


class QuoteRequestForm(AntiSpamFormMixin, forms.ModelForm):
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

    def clean_company_name(self):
        value = self.cleaned_data["company_name"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_contact_name(self):
        value = self.cleaned_data["contact_name"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_email(self):
        value = self.cleaned_data["email"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_message(self):
        value = self.cleaned_data.get("message", "").strip()
        reject_links(value)
        return value
