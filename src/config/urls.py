from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
    path("services/", include("apps.services.urls", namespace="services")),
    path("devis/", include("apps.quotes.urls", namespace="quotes")),
    path("flotte/", include("apps.fleet.urls", namespace="fleet")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
