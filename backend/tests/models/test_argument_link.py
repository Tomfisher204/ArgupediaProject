from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import (
    User,
    ArgumentScheme,
    CriticalQuestion,
    ArgumentLink
)


class ArgumentLinkModelTests(TestCase):
    """Tests for the ArgumentLink model."""

    def setUp(self):
        self.user = User.objects.create(
            username="link_user",
            first_name="Link",
            last_name="User",
            email="link_user@example.com",
            password="Password123"
        )
        self.parent_scheme = ArgumentScheme.objects.create(
            name="Parent Scheme",
            description="Parent argument scheme",
            created_by=self.user
        )
        self.child_scheme = ArgumentScheme.objects.create(
            name="Child Scheme",
            description="Child argument scheme",
            created_by=self.user
        )
        self.critical_question = CriticalQuestion.objects.create(
            scheme=self.parent_scheme,
            question="Is this reasoning logically valid?"
        )
        self.valid_link_data = {
            "parent_argument": self.parent_scheme,
            "child_argument": self.child_scheme,
            "critical_question": self.critical_question,
            "attacking": True
        }

    def test_create_argument_link(self):
        """Test that an ArgumentLink can be created successfully."""
        link = ArgumentLink.objects.create(**self.valid_link_data)
        self.assertEqual(link.parent_argument, self.parent_scheme)
        self.assertEqual(link.child_argument, self.child_scheme)
        self.assertEqual(link.critical_question, self.critical_question)
        self.assertTrue(link.attacking)
        self.assertIsNotNone(link.date_created)

    def test_attacking_default_true(self):
        """Test that attacking defaults to True."""
        link = ArgumentLink.objects.create(
            parent_argument=self.parent_scheme,
            child_argument=self.child_scheme,
            critical_question=self.critical_question
        )
        self.assertTrue(link.attacking)

    def test_argument_link_deleted_with_parent_scheme(self):
        """Test that ArgumentLink is deleted when parent scheme is deleted."""
        ArgumentLink.objects.create(**self.valid_link_data)
        self.parent_scheme.delete()
        self.assertEqual(ArgumentLink.objects.count(), 0)

    def test_argument_link_deleted_with_child_scheme(self):
        """Test that ArgumentLink is deleted when child scheme is deleted."""
        ArgumentLink.objects.create(**self.valid_link_data)
        self.child_scheme.delete()
        self.assertEqual(ArgumentLink.objects.count(), 0)

    def test_argument_link_deleted_with_critical_question(self):
        """Test that ArgumentLink is deleted when critical question is deleted."""
        ArgumentLink.objects.create(**self.valid_link_data)
        self.critical_question.delete()
        self.assertEqual(ArgumentLink.objects.count(), 0)

    def test_related_name_parent_links(self):
        """Test that related_name 'parent_links' works correctly."""
        link = ArgumentLink.objects.create(**self.valid_link_data)
        self.assertIn(link, self.parent_scheme.parent_links.all())
        self.assertEqual(self.parent_scheme.parent_links.count(), 1)

    def test_related_name_child_links(self):
        """Test that related_name 'child_links' works correctly."""
        link = ArgumentLink.objects.create(**self.valid_link_data)
        self.assertIn(link, self.child_scheme.child_links.all())
        self.assertEqual(self.child_scheme.child_links.count(), 1)

    def test_required_fields(self):
        """Test that required fields cannot be blank."""
        link = ArgumentLink(
            parent_argument=None,
            child_argument=self.child_scheme,
            critical_question=self.critical_question
        )
        with self.assertRaises(ValidationError):
            link.full_clean()