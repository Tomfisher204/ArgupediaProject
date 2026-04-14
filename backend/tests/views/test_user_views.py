from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User

def make_user(username="test_user", email="test@example.com"):
    return User.objects.create_user(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123",
    )

class RegisterViewTests(TestCase):
    """Tests for the RegisterView."""

    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'Password123',
            'first_name': 'New',
            'last_name': 'User',
        }

    def test_post_returns_201(self):
        response = self.client.post('/api/auth/register/', self.valid_data)
        self.assertEqual(response.status_code, 201)

    def test_post_creates_user(self):
        self.client.post('/api/auth/register/', self.valid_data)
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_duplicate_username_returns_400(self):
        make_user(username='new_user', email='other@example.com')
        response = self.client.post('/api/auth/register/', self.valid_data)
        self.assertEqual(response.status_code, 400)

    def test_duplicate_email_returns_400(self):
        make_user(username='other_user', email='new_user@example.com')
        response = self.client.post('/api/auth/register/', self.valid_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_required_fields_returns_400(self):
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            response = self.client.post('/api/auth/register/', data)
            self.assertEqual(response.status_code, 400)

    def test_short_password_returns_400(self):
        data = self.valid_data.copy()
        data['password'] = 'short'
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, 400)

    def test_register_does_not_require_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/auth/register/', self.valid_data)
        self.assertEqual(response.status_code, 201)

class MeViewTests(TestCase):
    """Tests for the MeView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_get_returns_200(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_correct_user(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_returns_expected_fields(self):
        response = self.client.get('/api/auth/me/')
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('argument_count', response.data)
        self.assertIn('reputation', response.data)
        self.assertIn('win_rate', response.data)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 401)