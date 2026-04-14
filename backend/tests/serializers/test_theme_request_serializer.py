from django.test import TestCase
from unittest.mock import MagicMock
from django.contrib.auth.models import AnonymousUser
from backend.models import User, ThemeRequest
from backend.serializers import ThemeRequestSerializer

def make_user(username="test_user", email="test@example.com"):
    return User.objects.create(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123",
    )

def make_request(user, title="Quantum Physics", reason="Needed for debates", **kwargs):
    return ThemeRequest.objects.create(requested_by=user, title=title, reason=reason, **kwargs)

def make_mock_request(user):
    mock_request = MagicMock()
    mock_request.user = user
    return mock_request

class ThemeRequestSerializerTests(TestCase):
    """Tests for the ThemeRequestSerializer."""

    def setUp(self):
        self.user = make_user()
        self.theme_request = make_request(self.user)

    def test_contains_expected_fields(self):
        serializer = ThemeRequestSerializer(self.theme_request)
        self.assertEqual(set(serializer.data.keys()), {'id', 'requested_by', 'title', 'description', 'reason', 'status', 'date_created', 'reviewed_at'})

    def test_requested_by_value(self):
        serializer = ThemeRequestSerializer(self.theme_request)
        self.assertEqual(serializer.data['requested_by'], self.user.id)

    def test_title_value(self):
        serializer = ThemeRequestSerializer(self.theme_request)
        self.assertEqual(serializer.data['title'], "Quantum Physics")

    def test_status_value(self):
        serializer = ThemeRequestSerializer(self.theme_request)
        self.assertEqual(serializer.data['status'], "pending")

    def test_reviewed_at_is_null_by_default(self):
        serializer = ThemeRequestSerializer(self.theme_request)
        self.assertIsNone(serializer.data['reviewed_at'])

    def test_read_only_fields_cannot_be_set(self):
        data = {
            'title': 'New Theme',
            'reason': 'A good reason',
            'requested_by': self.user.id,
            'status': 'approved',
        }
        serializer = ThemeRequestSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.status, 'pending')
        self.assertEqual(instance.requested_by, self.user)

    def test_create_sets_requested_by_from_context(self):
        data = {'title': 'Context Theme', 'reason': 'From context'}
        serializer = ThemeRequestSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.requested_by, self.user)

    def test_invalid_without_title(self):
        data = {'reason': 'Missing title'}
        serializer = ThemeRequestSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_invalid_without_reason(self):
        data = {'title': 'Missing reason'}
        serializer = ThemeRequestSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('reason', serializer.errors)