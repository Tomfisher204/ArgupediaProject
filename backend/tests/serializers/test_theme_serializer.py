from django.test import TestCase
from backend.models import User, ArgumentScheme, ArgumentTheme, Argument
from backend.serializers import ThemeSerializer

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

def make_theme(title="Science", creator=None):
    return ArgumentTheme.objects.create(
        title=title,
        creator=creator or make_user(username=f"tc_{title}", email=f"tc_{title}@example.com"),
    )

def make_argument(username, email, scheme, theme, root=False):
    return Argument.objects.create(
        author=make_user(username=username, email=email),
        scheme=scheme, theme=theme, root=root,
    )

class ThemeSerializerTests(TestCase):
    """Tests for the ThemeSerializer."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def test_contains_expected_fields(self):
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(set(serializer.data.keys()), {'id', 'title', 'description', 'date_created', 'argument_count'})

    def test_title_value(self):
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(serializer.data['title'], "Science")

    def test_argument_count_zero_with_no_arguments(self):
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(serializer.data['argument_count'], 0)

    def test_argument_count_only_counts_root_arguments(self):
        make_argument("root_author", "root@example.com", self.scheme, self.theme, root=True)
        make_argument("nonroot_author", "nonroot@example.com", self.scheme, self.theme, root=False)
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(serializer.data['argument_count'], 1)

    def test_argument_count_multiple_root_arguments(self):
        make_argument("root_1", "root1@example.com", self.scheme, self.theme, root=True)
        make_argument("root_2", "root2@example.com", self.scheme, self.theme, root=True)
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(serializer.data['argument_count'], 2)

    def test_argument_count_does_not_include_other_themes(self):
        other_theme = make_theme(title="Other Theme")
        make_argument("other_author", "other@example.com", self.scheme, other_theme, root=True)
        serializer = ThemeSerializer(self.theme)
        self.assertEqual(serializer.data['argument_count'], 0)

    def test_date_created_present(self):
        serializer = ThemeSerializer(self.theme)
        self.assertIsNotNone(serializer.data['date_created'])