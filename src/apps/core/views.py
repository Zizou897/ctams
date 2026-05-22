from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class HomeView(TemplateView):
    template_name = "core/home.html"


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([name, email, message]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return self.get(request, *args, **kwargs)

        send_mail(
            subject=f"[CTAMS] Message de {name}",
            message=f"De : {name} ({email} / {phone})\n\n{message}",
            from_email=None,
            recipient_list=["commercial@ctams.net"],
        )
        return redirect(reverse("core:contact") + "?sent=1")


class RobotsView(View):
    def get(self, request):
        content = "User-agent: *\nAllow: /\nSitemap: https://ctams.ci/sitemap.xml\n"
        return HttpResponse(content, content_type="text/plain")
