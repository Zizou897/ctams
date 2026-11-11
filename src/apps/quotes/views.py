from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from apps.core.antispam import is_rate_limited, make_timestamp_token
from apps.core.forms_utils import first_error_message
from .forms import QuoteRequestForm


class QuoteRequestView(FormView):
    template_name = "quotes/request.html"
    form_class = QuoteRequestForm
    success_url = reverse_lazy("quotes:confirmation")

    def get_initial(self):
        initial = super().get_initial()
        initial["horodatage"] = make_timestamp_token()
        return initial

    def post(self, request, *args, **kwargs):
        # Limite de fréquence par IP : dépassée => réponse silencieuse, rien n'est fait.
        if is_rate_limited(request, "quote-request"):
            return redirect(self.get_success_url())

        form = self.get_form()

        # Honeypot / délai de remplissage : robot détecté => réponse silencieuse.
        if form.is_bot():
            return redirect(self.get_success_url())

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        quote = form.save()
        send_mail(
            subject=f"[CTAMS] Nouvelle demande de devis — {quote.company_name}",
            message=self._build_email(quote),
            from_email=None,
            recipient_list=["commercial@ctams.net"],
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, first_error_message(form))
        return super().form_invalid(form)

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
