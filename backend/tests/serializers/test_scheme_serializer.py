from django.test import TestCase
from backend.models import User, ArgumentScheme, SchemeField, CriticalQuestion
from backend.serializers import ArgumentSchemeSerializer, SchemeFieldSerializer

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

class SchemeFieldSerializerTests(TestCase):
    """Tests for the SchemeFieldSerializer."""

    def setUp(self):
        self.scheme = make_scheme()
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)

    def test_contains_expected_fields(self):
        serializer = SchemeFieldSerializer(self.field)
        self.assertEqual(set(serializer.data.keys()), {'id', 'scheme', 'name', 'order'})

    def test_scheme_value(self):
        serializer = SchemeFieldSerializer(self.field)
        self.assertEqual(serializer.data['scheme'], self.scheme.id)

    def test_name_value(self):
        serializer = SchemeFieldSerializer(self.field)
        self.assertEqual(serializer.data['name'], "Premise")

    def test_order_value(self):
        serializer = SchemeFieldSerializer(self.field)
        self.assertEqual(serializer.data['order'], 1)

class ArgumentSchemeSerializerTests(TestCase):
    """Tests for the ArgumentSchemeSerializer."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        self.cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Is this valid?", two_way=False)

    def test_contains_expected_fields(self):
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(set(serializer.data.keys()), {'id', 'name', 'description', 'template', 'created_by', 'date_created', 'fields', 'critical_questions'})

    def test_name_value(self):
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(serializer.data['name'], self.scheme.name)

    def test_created_by_value(self):
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(serializer.data['created_by'], self.user.id)

    def test_fields_are_nested(self):
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(len(serializer.data['fields']), 1)
        self.assertEqual(serializer.data['fields'][0]['name'], "Premise")

    def test_critical_questions_are_nested(self):
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(len(serializer.data['critical_questions']), 1)
        self.assertEqual(serializer.data['critical_questions'][0]['question'], "Is this valid?")

    def test_multiple_fields_serialized(self):
        SchemeField.objects.create(scheme=self.scheme, name="Conclusion", order=2)
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(len(serializer.data['fields']), 2)

    def test_multiple_critical_questions_serialized(self):
        CriticalQuestion.objects.create(scheme=self.scheme, question="Another CQ?")
        serializer = ArgumentSchemeSerializer(self.scheme)
        self.assertEqual(len(serializer.data['critical_questions']), 2)

    def test_scheme_with_no_fields_or_questions(self):
        scheme = make_scheme(name="Empty Scheme", created_by=self.user)
        serializer = ArgumentSchemeSerializer(scheme)
        self.assertEqual(serializer.data['fields'], [])
        self.assertEqual(serializer.data['critical_questions'], [])