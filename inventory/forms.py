"""
Inventory form with server-side validation.

Even though the database and templates already protect us, we validate input
here too (whitelist the SKU format, trim names). Validating on the server is
the control that actually matters — client-side checks can be bypassed.
"""
import re

from django import forms

from .models import Item

# Whitelist: SKU = letters, digits and dashes, 3 to 40 characters.
SKU_PATTERN = re.compile(r"^[A-Z0-9\-]{3,40}$")


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "sku", "category", "description", "quantity", "unit_price"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Name is too short.")
        return name

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip().upper()
        if not SKU_PATTERN.match(sku):
            raise forms.ValidationError(
                "SKU may contain only letters, numbers and dashes (3–40 characters)."
            )
        return sku
