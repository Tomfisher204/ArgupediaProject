from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, ArgumentScheme, SchemeField, CriticalQuestion

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

class SchemeListViewTests(TestCase):
    """Tests for the SchemeListView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_get_returns_200(self):
        response = self.client.get('/api/schemes/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_all_schemes(self):
        make_scheme(name="Scheme A", created_by=self.user)
        make_scheme(name="Scheme B", created_by=self.user)
        response = self.client.get('/api/schemes/')
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/schemes/')
        self.assertEqual(response.status_code, 401)

    def test_schemes_include_fields(self):
        scheme = make_scheme(created_by=self.user)
        SchemeField.objects.create(scheme=scheme, name="Premise", order=1)
        response = self.client.get('/api/schemes/')
        scheme_data = next(s for s in response.data if s['id'] == scheme.id)
        self.assertEqual(len(scheme_data['fields']), 1)

    def test_schemes_include_critical_questions(self):
        scheme = make_scheme(created_by=self.user)
        CriticalQuestion.objects.create(scheme=scheme, question="Is this valid?")
        response = self.client.get('/api/schemes/')
        scheme_data = next(s for s in response.data if s['id'] == scheme.id)
        self.assertEqual(len(scheme_data['critical_questions']), 1)

    def test_schemes_ordered_by_name(self):
        make_scheme(name="Zebra Scheme", created_by=self.user)
        make_scheme(name="Alpha Scheme", created_by=self.user)
        response = self.client.get('/api/schemes/')
        names = [s['name'] for s in response.data]
        self.assertEqual(names, sorted(names))