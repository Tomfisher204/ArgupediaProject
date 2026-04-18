from django.test import TestCase
from unittest.mock import MagicMock
from backend.models import User, ArgumentScheme, ArgumentTheme, Argument
from backend.serializers import RegisterSerializer, UserSerializer

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create_user(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123", **kwargs,
    )

def make_scheme(name="Test Scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username=f"sc_{name}", email=f"sc_{name}@example.com"),
    )

def make_theme(title="Science", creator=None):
    return ArgumentTheme.objects.create(
        title=title,
        creator=creator or make_user(username=f"tc_{title}", email=f"tc_{title}@example.com"),
    )

def make_argument(username, email, scheme, theme, is_winning=None):
    return Argument.objects.create(
        author=make_user(username=username, email=email),
        scheme=scheme, theme=theme, is_winning=is_winning,
    )

class RegisterSerializerTests(TestCase):
    """Tests for the RegisterSerializer validation and user creation."""

    def setUp(self):
        self.valid_data = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'Password123',
            'first_name': 'New',
            'last_name': 'User',
        }

    def test_valid_data_is_valid(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_create_user(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'new_user')
        self.assertEqual(user.email, 'new_user@example.com')

    def test_password_too_short_is_invalid(self):
        data = self.valid_data.copy()
        data['password'] = 'short'
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_missing_required_fields_are_invalid(self):
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            serializer = RegisterSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_password_is_write_only(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        output = RegisterSerializer(user)
        self.assertNotIn('password', output.data)

class UserSerializerTests(TestCase):
    """Tests for the UserSerializer computed fields and output."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def test_contains_expected_fields(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(set(serializer.data.keys()), {'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_admin', 'argument_count', 'reputation', 'win_rate'})

    def test_argument_count_zero_with_no_arguments(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['argument_count'], 0)

    def test_argument_count_with_arguments(self):
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['argument_count'], 2)

    def test_win_rate_zero_with_no_arguments(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['win_rate'], 0)

    def test_win_rate_with_all_winning(self):
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=True)
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=True)
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['win_rate'], 100.0)

    def test_win_rate_with_mixed_results(self):
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=True)
        Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=False)
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['win_rate'], 50.0)

    def test_reputation_default_with_no_arguments(self):
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['reputation'], 5.0)

    def test_reputation_increases_with_wins(self):
        for i in range(5):
            Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=True)
        serializer = UserSerializer(self.user)
        self.assertGreater(serializer.data['reputation'], 5.0)

    def test_reputation_decreases_with_losses(self):
        for i in range(5):
            Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme, is_winning=False)
        serializer = UserSerializer(self.user)
        self.assertLess(serializer.data['reputation'], 5.0)