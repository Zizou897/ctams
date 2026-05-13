from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from .forms import QuoteRequestForm


class QuoteRequestView(FormView):
    template_name = "quotes/request.html"
    form_class = QuoteRequestForm
    success_url = reverse_lazy("quotes:confirmation")

    def form_valid(self, form):
        quote = form.save()
        send_mail(
            subject=f"[CTAMS] Nouvelle demande de devis — {quote.company_name}",
            message=self._build_email(quote),
            from_email=None,
            recipient_list=["Sasava221@gmail.com"],
        )
        return super().form_valid(form)

    def _build_email(self, quote):
        return (
            f"Entreprise : {quote.company_name}\n"
            f"Contact : {quote.contact_name} ({quote.email} / {quote.phone})\n"
            f"Véhicules : {quote.vehicle_count}\n"
            f"Service souhaité : {quote.service_type}\n\n"
            f"Message :\n{quote.message}"
        )


class QuoteConfirmationView(TemplateView):
    template_name = "quotes/confirmation.html"
