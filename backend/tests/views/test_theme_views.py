from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, ArgumentScheme, ArgumentTheme, Argument

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

def make_argument(author, scheme, theme, root=False):
    return Argument.objects.create(author=author, scheme=scheme, theme=theme, root=root)

class ThemeListViewTests(TestCase):
    """Tests for the ThemeListView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_get_returns_200(self):
        response = self.client.get('/api/themes/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_paginated_response(self):
        response = self.client.get('/api/themes/')
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/themes/')
        self.assertEqual(response.status_code, 401)

    def test_search_filters_by_title(self):
        make_theme(title="Quantum Physics")
        make_theme(title="Ancient History")
        response = self.client.get('/api/themes/?q=Quantum')
        titles = [t['title'] for t in response.data['results']]
        self.assertIn('Quantum Physics', titles)
        self.assertNotIn('Ancient History', titles)

    def test_search_filters_by_description(self):
        ArgumentTheme.objects.create(
            title="Philosophy", description="study of fundamental questions",
            creator=self.user,
        )
        make_theme(title="Biology")
        response = self.client.get('/api/themes/?q=fundamental')
        titles = [t['title'] for t in response.data['results']]
        self.assertIn('Philosophy', titles)
        self.assertNotIn('Biology', titles)

    def test_sort_alpha_asc(self):
        make_theme(title="Zebra")
        make_theme(title="Alpha")
        response = self.client.get('/api/themes/?sort=alpha_asc')
        titles = [t['title'] for t in response.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_sort_alpha_desc(self):
        make_theme(title="Zebra2")
        make_theme(title="Alpha2")
        response = self.client.get('/api/themes/?sort=alpha_desc')
        titles = [t['title'] for t in response.data['results']]
        self.assertEqual(titles, sorted(titles, reverse=True))

class ThemeArgumentsViewTests(TestCase):
    """Tests for the ThemeArgumentsView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def test_get_returns_200(self):
        response = self.client.get(f'/api/themes/{self.theme.id}/arguments/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_theme_data(self):
        response = self.client.get(f'/api/themes/{self.theme.id}/arguments/')
        self.assertIn('theme', response.data)
        self.assertEqual(response.data['theme']['id'], self.theme.id)

    def test_get_returns_only_root_arguments(self):
        make_argument(self.user, self.scheme, self.theme, root=True)
        make_argument(self.user, self.scheme, self.theme, root=False)
        response = self.client.get(f'/api/themes/{self.theme.id}/arguments/')
        self.assertEqual(len(response.data['arguments']), 1)

    def test_get_returns_404_for_nonexistent_theme(self):
        response = self.client.get('/api/themes/99999/arguments/')
        self.assertEqual(response.status_code, 404)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/themes/{self.theme.id}/arguments/')
        self.assertEqual(response.status_code, 401)

    def test_get_does_not_include_arguments_from_other_themes(self):
        other_theme = make_theme(title="Other Theme")
        make_argument(self.user, self.scheme, other_theme, root=True)
        make_argument(self.user, self.scheme, self.theme, root=True)
        response = self.client.get(f'/api/themes/{self.theme.id}/arguments/')
        self.assertEqual(len(response.data['arguments']), 1)