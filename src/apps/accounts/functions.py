from django.contrib.auth import get_user_model
from .models import ClientProfile

User = get_user_model()


def get_or_create_profile(user) -> ClientProfile:
    profile, _ = ClientProfile.objects.get_or_create(user=user)
    return profile
