from django.test import TestCase
from django.utils import timezone
from backend.models import User, ArgumentScheme, CriticalQuestion

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

def make_scheme(name="CQ Test Scheme"):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=make_user(username=f"creator_{name}", email=f"{name}@example.com"),
    )

class CriticalQuestionModelTests(TestCase):
    """Tests for the CriticalQuestion model validation and functionality."""

    def setUp(self):
        self.scheme = make_scheme()

    def test_create_critical_question(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Is the premise true?")
        self.assertEqual(cq.question, "Is the premise true?")
        self.assertEqual(cq.scheme, self.scheme)

    def test_two_way_defaults_to_false(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="One-way CQ?")
        self.assertFalse(cq.two_way)

    def test_two_way_can_be_set_true(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Two-way CQ?", two_way=True)
        self.assertTrue(cq.two_way)

    def test_date_created_auto_set(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Dated?")
        self.assertIsNotNone(cq.date_created)
        self.assertLessEqual(cq.date_created, timezone.now())

    def test_cascade_delete_with_scheme(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Will be deleted")
        cq_id = cq.id
        self.scheme.delete()
        self.assertFalse(CriticalQuestion.objects.filter(id=cq_id).exists())

    def test_multiple_questions_per_scheme(self):
        CriticalQuestion.objects.create(scheme=self.scheme, question="Q1?")
        CriticalQuestion.objects.create(scheme=self.scheme, question="Q2?")
        self.assertEqual(CriticalQuestion.objects.filter(scheme=self.scheme).count(), 2)