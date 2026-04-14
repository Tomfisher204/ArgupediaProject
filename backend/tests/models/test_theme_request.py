from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from backend.models import User, ThemeRequest

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

class ThemeRequestModelTests(TestCase):
    """Tests for the ThemeRequest model validation and functionality."""

    def setUp(self):
        self.user = make_user()
        self.valid_data = {
            "requested_by": self.user,
            "title": "Quantum Physics",
            "reason": "Needed for scientific debates",
        }

    def test_create_theme_request(self):
        request = ThemeRequest.objects.create(**self.valid_data)
        self.assertEqual(request.title, "Quantum Physics")
        self.assertEqual(request.requested_by, self.user)

    def test_status_defaults_to_pending(self):
        request = ThemeRequest.objects.create(**self.valid_data)
        self.assertEqual(request.status, "pending")

    def test_valid_status_choices(self):
        for status in ["pending", "approved", "rejected"]:
            data = self.valid_data.copy()
            data["title"] = f"Theme {status}"
            request = ThemeRequest.objects.create(**data, status=status)
            self.assertEqual(request.status, status)

    def test_description_is_optional(self):
        request = ThemeRequest.objects.create(**self.valid_data, description="")
        self.assertEqual(request.description, "")

    def test_reason_is_required(self):
        data = self.valid_data.copy()
        data["reason"] = ""
        request = ThemeRequest(**data)
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_title_max_length(self):
        data = self.valid_data.copy()
        data["title"] = "A" * 101
        request = ThemeRequest(**data)
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_date_created_auto_set(self):
        request = ThemeRequest.objects.create(**self.valid_data)
        self.assertIsNotNone(request.date_created)
        self.assertLessEqual(request.date_created, timezone.now())

    def test_reviewed_at_is_nullable(self):
        request = ThemeRequest.objects.create(**self.valid_data)
        self.assertIsNone(request.reviewed_at)

    def test_reviewed_at_can_be_set(self):
        review_time = timezone.now()
        request = ThemeRequest.objects.create(**self.valid_data, reviewed_at=review_time)
        self.assertIsNotNone(request.reviewed_at)

    def test_cascade_delete_with_user(self):
        user = make_user(username="req_user", email="req_user@example.com")
        request = ThemeRequest.objects.create(requested_by=user, title="Deletable", reason="Will be deleted")
        request_id = request.id
        user.delete()
        self.assertFalse(ThemeRequest.objects.filter(id=request_id).exists())

    def test_multiple_requests_per_user(self):
        ThemeRequest.objects.create(**self.valid_data)
        data2 = self.valid_data.copy()
        data2["title"] = "Second Theme"
        ThemeRequest.objects.create(**data2)
        self.assertEqual(ThemeRequest.objects.filter(requested_by=self.user).count(), 2)