"""
Management command: create demo accounts and sample inventory items.

Run with:  python manage.py seed_demo

It is safe to run more than once (uses get_or_create).
NOTE: these are DEMO credentials only. Change them before any real use.
"""
from django.core.management.base import BaseCommand

from accounts.models import User
from inventory.models import Item

DEMO_ITEMS = [
    # name, sku, category, quantity, unit_price
    ("Wireless Mouse", "WM-001", "ELECTRONICS", 40, "45.00"),
    ("Mechanical Keyboard", "KB-014", "ELECTRONICS", 18, "180.00"),
    ("Office Chair", "CH-220", "FURNITURE", 12, "320.50"),
    ("A4 Paper Ream", "PP-500", "STATIONERY", 200, "12.90"),
    ("Whiteboard Marker", "WM-777", "STATIONERY", 150, "3.50"),
    ("USB-C Cable 1m", "UC-101", "ELECTRONICS", 80, "19.90"),
    ("Bottled Water 500ml", "BW-050", "FOOD", 300, "1.20"),
]


class Command(BaseCommand):
    help = "Create demo admin/user accounts and sample inventory items."

    def handle(self, *args, **options):
        # --- Admin (also a Django superuser so /admin works) ---
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@demo.local",
                "role": User.Roles.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Admin@12345")
            admin.save()
            self.stdout.write("  created admin  / Admin@12345  (ADMIN)")
        else:
            self.stdout.write("  admin already exists")

        # --- Normal user ---
        staff, created = User.objects.get_or_create(
            username="staff1",
            defaults={"email": "staff1@demo.local", "role": User.Roles.USER},
        )
        if created:
            staff.set_password("Staff@12345")
            staff.save()
            self.stdout.write("  created staff1 / Staff@12345 (USER)")
        else:
            self.stdout.write("  staff1 already exists")

        # --- Sample items ---
        added = 0
        for name, sku, category, qty, price in DEMO_ITEMS:
            _, made = Item.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": category,
                    "quantity": qty,
                    "unit_price": price,
                    "created_by": admin,
                },
            )
            added += 1 if made else 0

        self.stdout.write(self.style.SUCCESS(f"Demo data ready ({added} new items)."))
