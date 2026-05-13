from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email *")
    company_name = forms.CharField(max_length=200, label="Nom de votre entreprise *")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "company_name", "phone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            from apps.accounts.models import ClientProfile
            ClientProfile.objects.create(
                user=user,
                company_name=self.cleaned_data["company_name"],
                phone=self.cleaned_data.get("phone", ""),
            )
        return user
