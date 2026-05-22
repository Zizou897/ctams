from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found

handler404 = "config.urls.custom_404"

def custom_404(request, exception):
    return page_not_found(request, exception, template_name="404.html")

urlpatterns = [
    path("admin/", admin.site.urls),
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
