"""
Inventory data model.

All database access in the app goes through the Django ORM (never raw SQL),
which uses parameterised queries and therefore protects against SQL injection.
"""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Item(models.Model):
    """A single stock item in the inventory."""

    class Category(models.TextChoices):
        ELECTRONICS = "ELECTRONICS", "Electronics"
        FURNITURE = "FURNITURE", "Furniture"
        STATIONERY = "STATIONERY", "Stationery"
        FOOD = "FOOD", "Food & Beverage"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=120)
    sku = models.CharField("SKU", max_length=40, unique=True)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("inventory:detail", args=[self.pk])

    @property
    def total_value(self):
        """Convenience value for display: quantity x unit price."""
        return self.quantity * self.unit_price
