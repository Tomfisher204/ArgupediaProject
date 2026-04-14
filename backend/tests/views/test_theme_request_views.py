from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, ThemeRequest

def make_user(username="test_user", email="test@example.com"):
    return User.objects.create(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123",
    )

class ThemeRequestViewTests(TestCase):
    """Tests for the ThemeRequestView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.valid_data = {'title': 'Quantum Physics', 'reason': 'Needed for debates'}

    def test_post_returns_201(self):
        response = self.client.post('/api/theme-requests/', self.valid_data)
        self.assertEqual(response.status_code, 201)

    def test_post_creates_theme_request(self):
        self.client.post('/api/theme-requests/', self.valid_data)
        self.assertTrue(ThemeRequest.objects.filter(title='Quantum Physics').exists())

    def test_post_sets_requested_by_from_auth_user(self):
        self.client.post('/api/theme-requests/', self.valid_data)
        request = ThemeRequest.objects.get(title='Quantum Physics')
        self.assertEqual(request.requested_by, self.user)

    def test_post_status_defaults_to_pending(self):
        self.client.post('/api/theme-requests/', self.valid_data)
        request = ThemeRequest.objects.get(title='Quantum Physics')
        self.assertEqual(request.status, 'pending')

    def test_post_missing_title_returns_400(self):
        response = self.client.post('/api/theme-requests/', {'reason': 'No title'})
        self.assertEqual(response.status_code, 400)

    def test_post_missing_reason_returns_400(self):
        response = self.client.post('/api/theme-requests/', {'title': 'No reason'})
        self.assertEqual(response.status_code, 400)

    def test_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/theme-requests/', self.valid_data)
        self.assertEqual(response.status_code, 401)