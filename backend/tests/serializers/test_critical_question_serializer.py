from django.test import TestCase
from backend.models import User, ArgumentScheme, CriticalQuestion
from backend.serializers import CriticalQuestionSerializer

def make_user(username="test_user", email="test@example.com"):
    return User.objects.create(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123",
    )

def make_scheme(name="Test Scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username=f"sc_{name}", email=f"sc_{name}@example.com"),
    )

def make_critical_question(scheme, question="Is this valid?", two_way=False):
    return CriticalQuestion.objects.create(scheme=scheme, question=question, two_way=two_way)

class CriticalQuestionSerializerTests(TestCase):
    """Tests for the CriticalQuestionSerializer."""

    def setUp(self):
        self.scheme = make_scheme()
        self.cq = make_critical_question(self.scheme)

    def test_contains_expected_fields(self):
        serializer = CriticalQuestionSerializer(self.cq)
        self.assertEqual(set(serializer.data.keys()), {'id', 'scheme', 'question', 'two_way', 'date_created'})

    def test_scheme_value(self):
        serializer = CriticalQuestionSerializer(self.cq)
        self.assertEqual(serializer.data['scheme'], self.scheme.id)

    def test_question_value(self):
        serializer = CriticalQuestionSerializer(self.cq)
        self.assertEqual(serializer.data['question'], "Is this valid?")

    def test_two_way_false_by_default(self):
        serializer = CriticalQuestionSerializer(self.cq)
        self.assertFalse(serializer.data['two_way'])

    def test_two_way_true(self):
        cq = make_critical_question(self.scheme, question="Two way?", two_way=True)
        serializer = CriticalQuestionSerializer(cq)
        self.assertTrue(serializer.data['two_way'])

    def test_date_created_present(self):
        serializer = CriticalQuestionSerializer(self.cq)
        self.assertIsNotNone(serializer.data['date_created'])