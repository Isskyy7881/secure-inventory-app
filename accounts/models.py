"""
Custom user model.

We extend Django's AbstractUser so we keep all the secure, battle-tested
auth behaviour (password hashing, permissions, etc.) and simply add a `role`
field to drive Role-Based Access Control (RBAC).
"""
import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


def avatar_upload_to(instance, filename):
    """
    Store avatars under media/avatars/ with a random UUID name.
    Renaming to a UUID stops users controlling the stored filename
    (path traversal / overwrite / guessable names).
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"avatars/{uuid.uuid4().hex}{ext}"


class User(AbstractUser):
    """Application user with a role used for access control."""

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        USER = "USER", "Normal User"

    # Email is required and unique (used for account recovery / identity).
    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)

    @property
    def is_admin(self):
        """True when this user has the administrator role."""
        return self.role == self.Roles.ADMIN

    def save(self, *args, **kwargs):
        # A Django superuser is always an administrator for RBAC purposes.
        if self.is_superuser:
            self.role = self.Roles.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
