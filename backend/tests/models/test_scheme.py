from django.test import TestCase
from django.utils import timezone
from backend.models import User, ArgumentScheme, SchemeField

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

def make_scheme(name="Test Scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username=f"creator_{name}", email=f"{name}@example.com"),
    )

class ArgumentSchemeModelTests(TestCase):
    """Tests for the ArgumentScheme model validation and functionality."""

    def setUp(self):
        self.user = make_user()

    def test_create_scheme(self):
        scheme = ArgumentScheme.objects.create(name="Modus Ponens", created_by=self.user)
        self.assertEqual(scheme.name, "Modus Ponens")
        self.assertEqual(scheme.created_by, self.user)

    def test_name_uniqueness(self):
        ArgumentScheme.objects.create(name="UniqueScheme", created_by=self.user)
        with self.assertRaises(Exception):
            ArgumentScheme.objects.create(name="UniqueScheme", created_by=self.user)

    def test_description_and_template_optional(self):
        scheme = ArgumentScheme.objects.create(name="Minimal", created_by=self.user, description="", template="")
        self.assertEqual(scheme.description, "")
        self.assertEqual(scheme.template, "")

    def test_date_created_auto_set(self):
        scheme = ArgumentScheme.objects.create(name="Dated Scheme", created_by=self.user)
        self.assertIsNotNone(scheme.date_created)
        self.assertLessEqual(scheme.date_created, timezone.now())

    def test_created_by_defaults_to_deleted_user_on_deletion(self):
        creator = make_user(username="scheme_del_user", email="scheme_del@example.com")
        scheme = ArgumentScheme.objects.create(name="Orphan Scheme", created_by=creator)
        creator.delete()
        scheme.refresh_from_db()
        self.assertEqual(scheme.created_by_id, User.deleted_user())

class SchemeFieldModelTests(TestCase):
    """Tests for the SchemeField model validation and functionality."""

    def setUp(self):
        self.scheme = make_scheme()

    def test_create_scheme_field(self):
        field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        self.assertEqual(field.name, "Premise")
        self.assertEqual(field.scheme, self.scheme)

    def test_default_order_is_zero(self):
        field = SchemeField.objects.create(scheme=self.scheme, name="No Order")
        self.assertEqual(field.order, 0)

    def test_fields_ordered_by_order_then_id(self):
        field_b = SchemeField.objects.create(scheme=self.scheme, name="B", order=2)
        field_a = SchemeField.objects.create(scheme=self.scheme, name="A", order=1)
        field_c = SchemeField.objects.create(scheme=self.scheme, name="C", order=2)
        fields = list(SchemeField.objects.filter(scheme=self.scheme))
        self.assertEqual(fields[0], field_a)
        self.assertEqual(fields[1], field_b)
        self.assertEqual(fields[2], field_c)

    def test_cascade_delete_with_scheme(self):
        field = SchemeField.objects.create(scheme=self.scheme, name="ToDelete", order=0)
        field_id = field.id
        self.scheme.delete()
        self.assertFalse(SchemeField.objects.filter(id=field_id).exists())

    def test_multiple_fields_per_scheme(self):
        SchemeField.objects.create(scheme=self.scheme, name="Field 1", order=1)
        SchemeField.objects.create(scheme=self.scheme, name="Field 2", order=2)
        self.assertEqual(SchemeField.objects.filter(scheme=self.scheme).count(), 2)