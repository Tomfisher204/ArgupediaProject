from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, ArgumentScheme, ArgumentTheme, SchemeField, CriticalQuestion, Argument, ArgumentLink

def make_user(username="test_user", email="test@example.com", is_admin=False):
    return User.objects.create(
        username=username, first_name="Test", last_name="User",
        email=email, password="Password123", is_admin=is_admin,
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

def make_argument(author, scheme, theme, **kwargs):
    return Argument.objects.create(author=author, scheme=scheme, theme=theme, **kwargs)

class ArgumentDetailViewTests(TestCase):
    """Tests for the ArgumentDetailView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.admin = make_user(username="admin", email="admin@example.com", is_admin=True)
        self.client.force_authenticate(user=self.user)
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = make_argument(self.user, self.scheme, self.theme)

    def test_get_returns_200(self):
        response = self.client.get(f'/api/arguments/{self.argument.id}/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_correct_argument(self):
        response = self.client.get(f'/api/arguments/{self.argument.id}/')
        self.assertEqual(response.data['id'], self.argument.id)

    def test_get_nonexistent_argument_returns_404(self):
        response = self.client.get('/api/arguments/99999/')
        self.assertEqual(response.status_code, 404)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/arguments/{self.argument.id}/')
        self.assertEqual(response.status_code, 401)

    def test_admin_can_delete_argument(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/arguments/{self.argument.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_removes_argument_from_db(self):
        self.client.force_authenticate(user=self.admin)
        argument_id = self.argument.id
        self.client.delete(f'/api/arguments/{self.argument.id}/')
        self.assertFalse(Argument.objects.filter(id=argument_id).exists())

    def test_non_admin_cannot_delete_argument(self):
        response = self.client.delete(f'/api/arguments/{self.argument.id}/')
        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_argument_returns_404(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/api/arguments/99999/')
        self.assertEqual(response.status_code, 404)

class CreateArgumentViewTests(TestCase):
    """Tests for the CreateArgumentView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        self.valid_data = {
            'scheme_id': self.scheme.id,
            'theme_id': self.theme.id,
            'field_values': [{'scheme_field_id': self.field.id, 'value': 'Test premise'}],
        }

    def test_post_returns_201(self):
        response = self.client.post('/api/arguments/create/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_post_creates_argument(self):
        self.client.post('/api/arguments/create/', self.valid_data, format='json')
        self.assertEqual(Argument.objects.filter(author=self.user).count(), 1)

    def test_post_returns_argument_id(self):
        response = self.client.post('/api/arguments/create/', self.valid_data, format='json')
        self.assertIn('id', response.data)

    def test_root_argument_has_root_flag_set(self):
        self.client.post('/api/arguments/create/', self.valid_data, format='json')
        argument = Argument.objects.get(author=self.user)
        self.assertTrue(argument.root)

    def test_child_argument_not_root(self):
        parent = make_argument(self.user, self.scheme, self.theme)
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")
        data = self.valid_data.copy()
        data['parent_argument_id'] = parent.id
        data['critical_question_id'] = cq.id
        self.client.post('/api/arguments/create/', data, format='json')
        child = Argument.objects.filter(author=self.user).exclude(id=parent.id).first()
        self.assertFalse(child.root)

    def test_child_argument_creates_link(self):
        parent = make_argument(self.user, self.scheme, self.theme)
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")
        data = self.valid_data.copy()
        data['parent_argument_id'] = parent.id
        data['critical_question_id'] = cq.id
        self.client.post('/api/arguments/create/', data, format='json')
        child = Argument.objects.filter(author=self.user).exclude(id=parent.id).first()
        self.assertTrue(ArgumentLink.objects.filter(parent_argument=parent, child_argument=child).exists())

    def test_invalid_data_returns_400(self):
        response = self.client.post('/api/arguments/create/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/arguments/create/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 401)

class UserArgumentsViewTests(TestCase):
    """Tests for the UserArgumentsView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def test_get_returns_200(self):
        response = self.client.get('/api/user/arguments/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_only_users_arguments(self):
        other_user = make_user(username="other", email="other@example.com")
        make_argument(self.user, self.scheme, self.theme)
        make_argument(other_user, self.scheme, self.theme)
        response = self.client.get('/api/user/arguments/')
        self.assertEqual(response.data['count'], 1)

    def test_get_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/user/arguments/')
        self.assertEqual(response.status_code, 401)

    def test_response_is_paginated(self):
        for i in range(5):
            make_argument(
                make_user(username=f"author_{i}", email=f"author_{i}@example.com"),
                self.scheme, self.theme
            )
        make_argument(self.user, self.scheme, self.theme)
        response = self.client.get('/api/user/arguments/')
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

class ReportArgumentViewTests(TestCase):
    """Tests for the ReportArgumentView."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = make_argument(self.user, self.scheme, self.theme)

    def test_post_reports_argument(self):
        response = self.client.post(f'/api/arguments/{self.argument.id}/report/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['reported'])

    def test_post_toggles_report_off(self):
        self.argument.reported_by.add(self.user)
        response = self.client.post(f'/api/arguments/{self.argument.id}/report/')
        self.assertFalse(response.data['reported'])

    def test_report_count_increments(self):
        response = self.client.post(f'/api/arguments/{self.argument.id}/report/')
        self.assertEqual(response.data['report_count'], 1)

    def test_report_count_decrements_on_toggle(self):
        self.argument.reported_by.add(self.user)
        response = self.client.post(f'/api/arguments/{self.argument.id}/report/')
        self.assertEqual(response.data['report_count'], 0)

    def test_returns_404_for_nonexistent_argument(self):
        response = self.client.post('/api/arguments/99999/report/')
        self.assertEqual(response.status_code, 404)

    def test_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f'/api/arguments/{self.argument.id}/report/')
        self.assertEqual(response.status_code, 401)