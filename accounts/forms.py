"""
Forms for registration and profile editing.

We build on Django's UserCreationForm so password strength validation and
secure hashing happen automatically. Extra server-side validation is added
for the email and the avatar upload.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

# Allowed image types and size limit for the profile avatar.
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB


class RegistrationForm(UserCreationForm):
    """Sign-up form: username + email + phone + password (x2)."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        # UserCreationForm adds password1 / password2 automatically.
        fields = ("username", "email", "phone")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        # Reject duplicates case-insensitively (defence in depth on top of the
        # database unique constraint).
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Lets a user edit their own profile details and avatar."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        # Only validate freshly uploaded files (they expose content_type/size).
        if avatar and hasattr(avatar, "content_type"):
            if avatar.size > MAX_AVATAR_SIZE:
                raise forms.ValidationError("Image must be 2 MB or smaller.")
            if avatar.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError(
                    "Only JPEG, PNG or WEBP images are allowed."
                )
        return avatar
