from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import User, ArgumentScheme, CriticalQuestion


class CriticalQuestionModelTests(TestCase):
    """Tests for the CriticalQuestion model."""

    def setUp(self):
        self.user = User.objects.create(
            username="john_smith",
            first_name="John",
            last_name="Smith",
            email="john.smith@example.com",
            password="Password123"
        )
        self.scheme = ArgumentScheme.objects.create(
            name="Argument from Authority",
            description="Arguments based on expert opinion.",
            created_by=self.user
        )
        self.valid_question_data = {
            "scheme": self.scheme,
            "question": "Is the authority cited truly an expert in this field?"
        }

    def test_create_critical_question(self):
        """Test that a CriticalQuestion can be created successfully."""
        question = CriticalQuestion.objects.create(**self.valid_question_data)
        self.assertEqual(question.scheme, self.scheme)
        self.assertEqual(
            question.question,
            "Is the authority cited truly an expert in this field?"
        )
        self.assertIsNotNone(question.date_created)

    def test_question_required(self):
        """Test that question field cannot be blank."""
        question = CriticalQuestion(
            scheme=self.scheme,
            question=""
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_scheme_required(self):
        """Test that scheme field is required."""
        question = CriticalQuestion(
            question="Some critical question?"
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_critical_questions_deleted_with_scheme(self):
        """Test that CriticalQuestions are deleted when the related scheme is deleted."""
        CriticalQuestion.objects.create(**self.valid_question_data)
        self.scheme.delete()
        self.assertEqual(CriticalQuestion.objects.count(), 0)

    def test_multiple_questions_per_scheme(self):
        """Test that multiple critical questions can belong to the same scheme."""
        q1 = CriticalQuestion.objects.create(
            scheme=self.scheme,
            question="Is the authority biased?"
        )
        q2 = CriticalQuestion.objects.create(
            scheme=self.scheme,
            question="Is the authority reliable?"
        )
        self.assertEqual(
            CriticalQuestion.objects.filter(scheme=self.scheme).count(),
            2
        )
        self.assertIn(q1, CriticalQuestion.objects.filter(scheme=self.scheme))
        self.assertIn(q2, CriticalQuestion.objects.filter(scheme=self.scheme))