from django import forms

from .antispam import AntiSpamFormMixin
from .models import ContactMessage
from .validators import reject_links, reject_links_html_and_newlines


class ContactForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        labels = {
            "name": "Nom complet",
            "email": "Email professionnel",
            "phone": "Téléphone",
            "message": "Votre besoin",
        }

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_email(self):
        value = self.cleaned_data["email"].strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_phone(self):
        value = self.cleaned_data.get("phone", "").strip()
        reject_links_html_and_newlines(value)
        return value

    def clean_message(self):
        value = self.cleaned_data["message"].strip()
        reject_links(value)
        return value
