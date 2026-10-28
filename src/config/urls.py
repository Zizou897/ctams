from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import StaticViewSitemap, ServiceSitemap
from apps.core.api_views import ContactMessageListAPIView
from apps.quotes.api_views import DevisListAPIView, QuoteRequestListAPIView

ADMIN_URL = getattr(settings, "ADMIN_URL", "gestion-bo-ctams/")

handler404 = "config.urls.custom_404"

def custom_404(request, exception):
    return page_not_found(request, exception, template_name="404.html")

sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
}

# API interne en lecture seule, protégée par clé API (settings.INTERNAL_API_KEY),
# consommée par atelierProjet — jamais par le site public.
internal_api_patterns = [
    path("contact-messages/", ContactMessageListAPIView.as_view(), name="contact-messages"),
    path("quote-requests/", QuoteRequestListAPIView.as_view(), name="quote-requests"),
    path("devis/", DevisListAPIView.as_view(), name="devis"),
]

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path("internal-api/", include((internal_api_patterns, "internal_api"))),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("tinymce/", include("tinymce.urls")),
    path("", include("apps.core.urls", namespace="core")),
    path("services/", include("apps.services.urls", namespace="services")),
    path("devis/", include("apps.quotes.urls", namespace="quotes")),
    path("flotte/", include("apps.fleet.urls", namespace="fleet")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("404/", lambda r: custom_404(r, None))]
