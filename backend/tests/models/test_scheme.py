from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import User, ArgumentScheme, SchemeField


class ArgumentSchemeModelTests(TestCase):
    """Tests for the ArgumentScheme and SchemeField models."""

    def setUp(self):
        self.user = User.objects.create(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="Password123"
        )
        self.valid_scheme_data = {
            "name": "Causal Argument",
            "description": "Arguments based on cause and effect.",
            "created_by": self.user
        }

    def test_create_argument_scheme(self):
        """Test that an ArgumentScheme can be created successfully."""
        scheme = ArgumentScheme.objects.create(**self.valid_scheme_data)
        self.assertEqual(scheme.name, "Causal Argument")
        self.assertEqual(scheme.description, "Arguments based on cause and effect.")
        self.assertEqual(scheme.created_by, self.user)
        self.assertIsNotNone(scheme.date_created)

    def test_name_uniqueness(self):
        """Test that scheme name must be unique."""
        ArgumentScheme.objects.create(**self.valid_scheme_data)
        duplicate_scheme = ArgumentScheme(**self.valid_scheme_data)
        with self.assertRaises(Exception):
            duplicate_scheme.save()

    def test_blank_description_allowed(self):
        """Test that description can be blank."""
        scheme_data = self.valid_scheme_data.copy()
        scheme_data["name"] = "Analogical Argument"
        scheme_data["description"] = ""
        scheme = ArgumentScheme(**scheme_data)
        scheme.full_clean()

    def test_created_by_default_deleted_user(self):
        """Test that created_by defaults to deleted_user if not provided."""
        scheme = ArgumentScheme.objects.create(name="Ethical Argument")
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(scheme.created_by, deleted_user)

    def test_created_by_set_default_on_user_delete(self):
        """Test that created_by is set to deleted_user when original creator is deleted."""
        scheme = ArgumentScheme.objects.create(**self.valid_scheme_data)
        self.user.delete()
        scheme.refresh_from_db()
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(scheme.created_by, deleted_user)


class SchemeFieldModelTests(TestCase):
    """Tests for the SchemeField model."""

    def setUp(self):
        self.user = User.objects.create(
            username="jane_doe",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="Password123"
        )
        self.scheme = ArgumentScheme.objects.create(
            name="Practical Reasoning",
            description="Reasoning about actions.",
            created_by=self.user
        )

    def test_create_scheme_field(self):
        """Test that a SchemeField can be created successfully."""
        field = SchemeField.objects.create(
            scheme=self.scheme,
            name="Premise"
        )
        self.assertEqual(field.scheme, self.scheme)
        self.assertEqual(field.name, "Premise")

    def test_scheme_field_requires_name(self):
        """Test that name cannot be blank."""
        field = SchemeField(
            scheme=self.scheme,
            name=""
        )
        with self.assertRaises(ValidationError):
            field.full_clean()

    def test_scheme_related_name_fields(self):
        """Test that related_name 'fields' works correctly."""
        field1 = SchemeField.objects.create(
            scheme=self.scheme,
            name="Premise"
        )
        field2 = SchemeField.objects.create(
            scheme=self.scheme,
            name="Conclusion"
        )
        self.assertIn(field1, self.scheme.fields.all())
        self.assertIn(field2, self.scheme.fields.all())
        self.assertEqual(self.scheme.fields.count(), 2)

    def test_scheme_field_deleted_with_scheme(self):
        """Test that SchemeFields are deleted when the parent scheme is deleted."""
        SchemeField.objects.create(
            scheme=self.scheme,
            name="Premise"
        )
        self.scheme.delete()
        self.assertEqual(SchemeField.objects.count(), 0)