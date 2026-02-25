from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission
from backend.models import User


class UserModelTests(TestCase):
    """Tests for the custom User model validation and functionality."""

    def setUp(self):
        self.valid_user_data = {
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "Password123"
        }

    def test_username_uniqueness(self):
        """Test that username must be unique."""
        User.objects.create(**self.valid_user_data)
        duplicate_user = User(**self.valid_user_data)
        with self.assertRaises(Exception):
            duplicate_user.save()

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        User.objects.create(**self.valid_user_data)
        user_data = self.valid_user_data.copy()
        user_data["username"] = "another_user"
        duplicate_email_user = User(**user_data)
        with self.assertRaises(Exception):
            duplicate_email_user.save()

    def test_email_validation(self):
        """Test that email validation enforces a valid format."""
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
        """Test that password validation requires minimum length, uppercase letters, and numbers."""
        valid_passwords = ["Password123", "Test1234", "Admin999"]
        for password in valid_passwords:
            user_data = self.valid_user_data.copy()
            user_data["username"] = f"user_{password}"
            user_data["password"] = password
            user = User(**user_data)
            user.full_clean()
        invalid_passwords = ["password", "12345678", "Password", "test123", "Short1"]
        for password in invalid_passwords:
            user = User(
                username=f"user_invalid_{password}",
                first_name=self.valid_user_data["first_name"],
                last_name=self.valid_user_data["last_name"],
                email=f"invalid_{password}@example.com",
                password=password
            )
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_required_fields(self):
        """Test that required fields cannot be blank."""
        required_fields = ["username", "first_name", "last_name", "email", "password"]
        for field in required_fields:
            user_data = self.valid_user_data.copy()
            user_data[field] = ""
            user = User(**user_data)
            with self.assertRaises(ValidationError):
                user.full_clean()

    def test_is_admin_default(self):
        """Test that is_admin defaults to False."""
        user = User.objects.create(**self.valid_user_data)
        self.assertFalse(user.is_admin)

    def test_is_admin_field(self):
        """Test that the is_admin field correctly identifies admin status."""
        admin_data = self.valid_user_data.copy()
        admin_data["username"] = "admin_user"
        admin_data["email"] = "admin@example.com"
        admin_data["is_admin"] = True
        admin_user = User.objects.create(**admin_data)
        self.assertTrue(admin_user.is_admin)

    def test_groups_and_permissions_relationship(self):
        """Test custom related names for groups and permissions."""
        user = User.objects.create(**self.valid_user_data)
        group = Group.objects.create(name="Test Group")
        permission = Permission.objects.first()
        user.groups.add(group)
        user.user_permissions.add(permission)
        self.assertIn(group, user.groups.all())
        self.assertIn(permission, user.user_permissions.all())

    def test_deleted_user_method(self):
        """Test that deleted_user class method returns consistent user ID."""
        deleted_user_id_first = User.deleted_user()
        deleted_user_id_second = User.deleted_user()
        self.assertEqual(deleted_user_id_first, deleted_user_id_second)
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(deleted_user.first_name, "Deleted")
        self.assertEqual(deleted_user.last_name, "User")
        self.assertEqual(deleted_user.email, "deleted@example.com")