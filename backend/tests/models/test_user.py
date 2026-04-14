from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission
from backend.models import User

def make_user(username="john_doe", email="john.doe@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="John",
        last_name="Doe",
        email=email,
        password="Password123",
        **kwargs,
    )

class UserModelTests(TestCase):
    """Tests for the custom User model validation and functionality."""

    def setUp(self):
        self.valid_user_data = {
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "Password123",
        }

    def test_username_uniqueness(self):
        make_user()
        duplicate_user = User(**self.valid_user_data)
        with self.assertRaises(Exception):
            duplicate_user.save()

    def test_email_uniqueness(self):
        make_user()
        user_data = self.valid_user_data.copy()
        user_data["username"] = "another_user"
        duplicate_email_user = User(**user_data)
        with self.assertRaises(Exception):
            duplicate_email_user.save()

    def test_email_validation(self):
        valid_user = User(**self.valid_user_data)
        valid_user.full_clean()
        invalid_emails = ["john.doeexample.com", "john@", "@example.com", "john@com"]
        for email in invalid_emails:
            user_data = self.valid_user_data.copy()
            user_data["username"] = f"user_{email}"
            user_data["email"] = email
            user = User(**user_data)
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_password_validation(self):
        valid_passwords = ["Password123", "Test1234", "Admin999"]
        for password in valid_passwords:
            user_data = self.valid_user_data.copy()
            user_data["username"] = f"user_{password}"
            user_data["email"] = f"{password}@example.com"
            user = User(**user_data)
            user.full_clean()
        invalid_passwords = ["password", "12345678", "Password", "test123", "Short1"]
        for password in invalid_passwords:
            user = User(
                username=f"user_invalid_{password}",
                first_name=self.valid_user_data["first_name"],
                last_name=self.valid_user_data["last_name"],
                email=f"invalid_{password}@example.com",
                password=password,
            )
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_required_fields(self):
        required_fields = ["username", "first_name", "last_name", "email", "password"]
        for field in required_fields:
            user_data = self.valid_user_data.copy()
            user_data[field] = ""
            user = User(**user_data)
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_is_admin_default(self):
        user = make_user()
        self.assertFalse(user.is_admin)

    def test_is_admin_field(self):
        user = make_user(username="admin_user", email="admin@example.com", is_admin=True)
        self.assertTrue(user.is_admin)

    def test_groups_and_permissions_relationship(self):
        user = make_user()
        group = Group.objects.create(name="Test Group")
        permission = Permission.objects.first()
        user.groups.add(group)
        user.user_permissions.add(permission)
        self.assertIn(group, user.groups.all())
        self.assertIn(permission, user.user_permissions.all())

    def test_deleted_user_method_returns_consistent_id(self):
        first = User.deleted_user()
        second = User.deleted_user()
        self.assertEqual(first, second)

    def test_deleted_user_has_correct_fields(self):
        User.deleted_user()
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(deleted_user.first_name, "Deleted")
        self.assertEqual(deleted_user.last_name, "User")
        self.assertEqual(deleted_user.email, "deleted@example.com")

    def test_username_max_length(self):
        user_data = self.valid_user_data.copy()
        user_data["username"] = "a" * 51
        user = User(**user_data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_first_name_max_length(self):
        user_data = self.valid_user_data.copy()
        user_data["first_name"] = "a" * 51
        user = User(**user_data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_last_name_max_length(self):
        user_data = self.valid_user_data.copy()
        user_data["last_name"] = "a" * 51
        user = User(**user_data)
        with self.assertRaises(ValidationError):
            user.full_clean()