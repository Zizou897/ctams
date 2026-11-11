from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .antispam import is_rate_limited, make_timestamp_token
from .forms import ContactForm
from .forms_utils import first_error_message


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["partners_api_url"] = settings.CTAMS_PARTNERS_API_URL
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", ContactForm(initial={"horodatage": make_timestamp_token()}))
        return context

    def post(self, request, *args, **kwargs):
        success_url = reverse("core:contact") + "?sent=1"

        # Limite de fréquence par IP : dépassée => réponse silencieuse, rien n'est fait.
        if is_rate_limited(request, "contact"):
            return redirect(success_url)

        form = ContactForm(request.POST)

        # Honeypot / délai de remplissage : robot détecté => réponse silencieuse.
        if form.is_bot():
            return redirect(success_url)

        if not form.is_valid():
            messages.error(request, first_error_message(form))
            return self.get(request, *args, **kwargs)

        contact = form.save()

        send_mail(
            subject=f"[CTAMS] Message de {contact.name}",
            message=f"De : {contact.name} ({contact.email} / {contact.phone})\n\n{contact.message}",
            from_email=None,
            recipient_list=["commercial@ctams.net"],
        )
        return redirect(success_url)


class RobotsView(View):
    def get(self, request):
        content = "User-agent: *\nAllow: /\nSitemap: https://ctams.net/sitemap.xml\n"
        return HttpResponse(content, content_type="text/plain")
