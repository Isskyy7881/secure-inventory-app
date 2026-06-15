"""
Tests that prove the functional + access-control requirements work.

These double as evidence for the report (RBAC enforced, audit logging works).
Run with:  python manage.py test
"""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from auditlog.models import AuditLog
from inventory.models import Item


class RBACTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin1", "a@example.com", "Admin@12345", role=User.Roles.ADMIN
        )
        self.user = User.objects.create_user(
            "user1", "u@example.com", "User@12345"
        )
        self.item = Item.objects.create(
            name="Pen", sku="PEN-001", quantity=5, unit_price=1
        )

    def test_anonymous_is_redirected_to_login(self):
        resp = self.client.get(reverse("inventory:list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp.url)

    def test_normal_user_cannot_open_add_page(self):
        self.client.login(username="user1", password="User@12345")
        resp = self.client.get(reverse("inventory:add"))
        self.assertEqual(resp.status_code, 403)  # blocked by RBAC

    def test_admin_can_open_add_page(self):
        self.client.login(username="admin1", password="Admin@12345")
        resp = self.client.get(reverse("inventory:add"))
        self.assertEqual(resp.status_code, 200)

    def test_normal_user_can_view_list(self):
        self.client.login(username="user1", password="User@12345")
        resp = self.client.get(reverse("inventory:list"))
        self.assertEqual(resp.status_code, 200)

    def test_admin_create_item_writes_audit_log(self):
        self.client.login(username="admin1", password="Admin@12345")
        self.client.post(
            reverse("inventory:add"),
            {
                "name": "Book",
                "sku": "BOOK-001",
                "category": "OTHER",
                "description": "",
                "quantity": 3,
                "unit_price": "9.90",
            },
        )
        self.assertTrue(Item.objects.filter(sku="BOOK-001").exists())
        self.assertTrue(AuditLog.objects.filter(action="ITEM_CREATE").exists())

    def test_blocked_access_is_logged(self):
        self.client.login(username="user1", password="User@12345")
        self.client.get(reverse("inventory:add"))
        self.assertTrue(AuditLog.objects.filter(action="ACCESS_DENIED").exists())


class AuthTests(TestCase):
    def test_failed_login_is_logged(self):
        User.objects.create_user("bob", "b@example.com", "Bob@123456")
        self.client.post(
            reverse("login"), {"username": "bob", "password": "wrong-password"}
        )
        self.assertTrue(AuditLog.objects.filter(action="LOGIN_FAILED").exists())

    def test_successful_login_is_logged(self):
        User.objects.create_user("carol", "c@example.com", "Carol@12345")
        self.client.post(
            reverse("login"), {"username": "carol", "password": "Carol@12345"}
        )
        self.assertTrue(AuditLog.objects.filter(action="LOGIN_SUCCESS").exists())

    def test_sku_whitelist_rejects_bad_input(self):
        admin = User.objects.create_user(
            "admin2", "a2@example.com", "Admin@12345", role=User.Roles.ADMIN
        )
        self.client.force_login(admin)
        resp = self.client.post(
            reverse("inventory:add"),
            {
                "name": "Bad",
                "sku": "bad sku!!",  # spaces + symbols -> rejected
                "category": "OTHER",
                "description": "",
                "quantity": 1,
                "unit_price": "1.00",
            },
        )
        # Form re-rendered with errors (200), item NOT created.
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Item.objects.filter(name="Bad").exists())
