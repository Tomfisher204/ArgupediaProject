from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import User, ArgumentTheme


class ArgumentThemeModelTests(TestCase):
    """Tests for the ArgumentTheme model validation and functionality."""

    def setUp(self):
        self.user = User.objects.create(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="Password123"
        )
        self.valid_theme_data = {
            "title": "Politics",
            "description": "Political discussions and debates.",
            "creator": self.user
        }

    def test_create_argument_theme(self):
        """Test that an ArgumentTheme can be created successfully."""
        theme = ArgumentTheme.objects.create(**self.valid_theme_data)
        self.assertEqual(theme.title, "Politics")
        self.assertEqual(theme.description, "Political discussions and debates.")
        self.assertEqual(theme.creator, self.user)
        self.assertIsNotNone(theme.date_created)

    def test_title_uniqueness(self):
        """Test that title must be unique."""
        ArgumentTheme.objects.create(**self.valid_theme_data)
        duplicate_theme = ArgumentTheme(**self.valid_theme_data)
        with self.assertRaises(Exception):
            duplicate_theme.save()

    def test_blank_description_allowed(self):
        """Test that description can be blank."""
        theme_data = self.valid_theme_data.copy()
        theme_data["title"] = "Technology"
        theme_data["description"] = ""
        theme = ArgumentTheme(**theme_data)
        theme.full_clean()

    def test_default_title_value(self):
        """Test that default title is 'Other'."""
        theme = ArgumentTheme.objects.create(creator=self.user)
        self.assertEqual(theme.title, "Other")

    def test_creator_default_deleted_user(self):
        """Test that creator defaults to deleted_user if not provided."""
        theme = ArgumentTheme.objects.create(title="Science")
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(theme.creator, deleted_user)

    def test_creator_set_default_on_user_delete(self):
        """Test that creator is set to deleted_user when original creator is deleted."""
        theme = ArgumentTheme.objects.create(**self.valid_theme_data)
        self.user.delete()
        theme.refresh_from_db()
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(theme.creator, deleted_user)

    def test_get_or_create_other_theme(self):
        """Test get_or_create_other_theme returns the same 'Other' instance."""
        theme_first = ArgumentTheme.get_or_create_other_theme()
        theme_second = ArgumentTheme.get_or_create_other_theme()
        self.assertEqual(theme_first.id, theme_second.id)
        self.assertEqual(theme_first.title, "Other")

    def test_required_title_field(self):
        """Test that title cannot be blank."""
        theme = ArgumentTheme(
            title="",
            description="Some description",
            creator=self.user
        )
        with self.assertRaises(ValidationError):
            theme.full_clean()