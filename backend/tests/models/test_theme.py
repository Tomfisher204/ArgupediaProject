from django.test import TestCase
from django.utils import timezone
from backend.models import User, ArgumentTheme

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

class ArgumentThemeModelTests(TestCase):
    """Tests for the ArgumentTheme model validation and functionality."""

    def setUp(self):
        self.user = make_user()

    def test_create_theme(self):
        theme = ArgumentTheme.objects.create(title="Philosophy", creator=self.user)
        self.assertEqual(theme.title, "Philosophy")
        self.assertEqual(theme.creator, self.user)

    def test_title_uniqueness(self):
        ArgumentTheme.objects.create(title="UniqueTheme", creator=self.user)
        with self.assertRaises(Exception):
            ArgumentTheme.objects.create(title="UniqueTheme", creator=self.user)

    def test_description_is_optional(self):
        theme = ArgumentTheme.objects.create(title="No Desc", creator=self.user, description="")
        self.assertEqual(theme.description, "")

    def test_date_created_auto_set(self):
        theme = ArgumentTheme.objects.create(title="Dated", creator=self.user)
        self.assertIsNotNone(theme.date_created)
        self.assertLessEqual(theme.date_created, timezone.now())

    def test_get_or_create_other_theme_creates_once(self):
        first = ArgumentTheme.get_or_create_other_theme()
        second = ArgumentTheme.get_or_create_other_theme()
        self.assertEqual(first, second)

    def test_get_or_create_other_theme_title(self):
        ArgumentTheme.get_or_create_other_theme()
        other_theme = ArgumentTheme.objects.get(title="Other")
        self.assertEqual(other_theme.title, "Other")

    def test_creator_set_to_deleted_user_on_user_deletion(self):
        creator = make_user(username="creator_to_delete", email="creator_del@example.com")
        theme = ArgumentTheme.objects.create(title="Orphaned Theme", creator=creator)
        creator.delete()
        theme.refresh_from_db()
        self.assertEqual(theme.creator_id, User.deleted_user())