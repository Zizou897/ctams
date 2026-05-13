from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.QuoteRequestView.as_view(), name="request"),
    path("confirmation/", views.QuoteConfirmationView.as_view(), name="confirmation"),
]
