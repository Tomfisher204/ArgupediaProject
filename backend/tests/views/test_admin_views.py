from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, ArgumentScheme, ArgumentTheme, CriticalQuestion, Argument, ThemeRequest

def make_user(username="test_user", email="test@example.com", is_admin=False):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        is_admin=is_admin,
    )

def make_admin(username="admin_user", email="admin@example.com"):
    return make_user(username=username, email=email, is_admin=True)

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

def make_argument(author, scheme, theme):
    return Argument.objects.create(author=author, scheme=scheme, theme=theme)

def make_theme_request(user, title="New Theme", reason="Good reason"):
    return ThemeRequest.objects.create(requested_by=user, title=title, reason=reason)

class AdminStatsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)

    def test_returns_200_for_admin(self):
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.status_code, 200)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=make_user(username="regular", email="regular@example.com"))
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.status_code, 403)

    def test_returns_401_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.status_code, 401)

    def test_response_contains_expected_fields(self):
        response = self.client.get('/api/admin/stats/')
        self.assertIn('total_users', response.data)
        self.assertIn('total_arguments', response.data)
        self.assertIn('total_themes', response.data)
        self.assertIn('pending_theme_requests', response.data)

    def test_counts_are_correct(self):
        make_user(username="extra_user", email="extra@example.com")
        make_theme_request(self.admin)
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.data['pending_theme_requests'], 1)

class AdminThemeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)
        self.theme = make_theme()

    def test_delete_theme_returns_204(self):
        response = self.client.delete(f'/api/admin/theme/{self.theme.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_theme_removes_from_db(self):
        theme_id = self.theme.id
        self.client.delete(f'/api/admin/theme/{self.theme.id}/')
        self.assertFalse(ArgumentTheme.objects.filter(id=theme_id).exists())

    def test_delete_nonexistent_theme_returns_404(self):
        response = self.client.delete('/api/admin/theme/99999/')
        self.assertEqual(response.status_code, 404)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=make_user(username="regular", email="regular@example.com"))
        response = self.client.delete(f'/api/admin/theme/{self.theme.id}/')
        self.assertEqual(response.status_code, 403)

class AdminThemeRequestsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)
        self.user = make_user(username="requester", email="requester@example.com")
        self.theme_request = make_theme_request(self.user)

    def test_get_returns_200(self):
        response = self.client.get('/api/admin/theme-requests/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_only_pending_requests(self):
        ThemeRequest.objects.create(requested_by=self.user, title="Approved", reason="r", status='approved')
        response = self.client.get('/api/admin/theme-requests/')
        for item in response.data['results']:
            self.assertEqual(item['status'], 'pending')

    def test_get_response_contains_expected_fields(self):
        response = self.client.get('/api/admin/theme-requests/')
        item = response.data['results'][0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('reason', item)
        self.assertIn('requested_by', item)

    def test_approve_action_creates_theme(self):
        response = self.client.post('/api/admin/theme-requests/', {
            'request_id': self.theme_request.id,
            'action': 'approve'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ArgumentTheme.objects.filter(title=self.theme_request.title).exists())

    def test_approve_action_updates_status(self):
        self.client.post('/api/admin/theme-requests/', {
            'request_id': self.theme_request.id,
            'action': 'approve'
        })
        self.theme_request.refresh_from_db()
        self.assertEqual(self.theme_request.status, 'approved')

    def test_reject_action_updates_status(self):
        self.client.post('/api/admin/theme-requests/', {
            'request_id': self.theme_request.id,
            'action': 'reject'
        })
        self.theme_request.refresh_from_db()
        self.assertEqual(self.theme_request.status, 'rejected')

    def test_invalid_action_returns_400(self):
        response = self.client.post('/api/admin/theme-requests/', {
            'request_id': self.theme_request.id,
            'action': 'invalid'
        })
        self.assertEqual(response.status_code, 400)

    def test_missing_fields_returns_400(self):
        response = self.client.post('/api/admin/theme-requests/', {})
        self.assertEqual(response.status_code, 400)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/admin/theme-requests/')
        self.assertEqual(response.status_code, 403)

class AdminReportedArgumentsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)
        self.scheme = make_scheme(created_by=self.admin)
        self.theme = make_theme(creator=self.admin)
        self.user = make_user(username="reporter", email="reporter@example.com")
        self.argument = make_argument(self.admin, self.scheme, self.theme)

    def test_get_returns_200(self):
        self.argument.reported_by.add(self.user)
        response = self.client.get('/api/admin/reported-arguments/')
        self.assertEqual(response.status_code, 200)

    def test_only_reported_arguments_returned(self):
        unreported = make_argument(self.admin, self.scheme, self.theme)
        self.argument.reported_by.add(self.user)
        response = self.client.get('/api/admin/reported-arguments/')
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.argument.id, ids)
        self.assertNotIn(unreported.id, ids)

    def test_response_contains_expected_fields(self):
        self.argument.reported_by.add(self.user)
        response = self.client.get('/api/admin/reported-arguments/')
        item = response.data['results'][0]
        self.assertIn('id', item)
        self.assertIn('report_count', item)
        self.assertIn('author', item)
        self.assertIn('field_values', item)

    def test_report_count_is_correct(self):
        self.argument.reported_by.add(self.user)
        response = self.client.get('/api/admin/reported-arguments/')
        self.assertEqual(response.data['results'][0]['report_count'], 1)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/admin/reported-arguments/')
        self.assertEqual(response.status_code, 403)

class AdminSchemesViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)

    def test_get_returns_200(self):
        response = self.client.get('/api/admin/schemes/')
        self.assertEqual(response.status_code, 200)

    def test_get_returns_all_schemes(self):
        make_scheme(name="Scheme A", created_by=self.admin)
        make_scheme(name="Scheme B", created_by=self.admin)
        response = self.client.get('/api/admin/schemes/')
        self.assertGreaterEqual(len(response.data), 2)

    def test_post_creates_scheme(self):
        response = self.client.post('/api/admin/schemes/', {
            'name': 'New Scheme',
            'template': 'Because **Premise**, therefore **Conclusion**.'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ArgumentScheme.objects.filter(name='New Scheme').exists())

    def test_post_missing_name_returns_400(self):
        response = self.client.post('/api/admin/schemes/', {
            'template': 'Some **field**.'
        })
        self.assertEqual(response.status_code, 400)

    def test_post_missing_template_returns_400(self):
        response = self.client.post('/api/admin/schemes/', {
            'name': 'No Template'
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_scheme_returns_204(self):
        scheme = make_scheme(name="To Delete", created_by=self.admin)
        response = self.client.delete(f'/api/admin/schemes/{scheme.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_scheme_removes_from_db(self):
        scheme = make_scheme(name="To Delete 2", created_by=self.admin)
        scheme_id = scheme.id
        self.client.delete(f'/api/admin/schemes/{scheme.id}/')
        self.assertFalse(ArgumentScheme.objects.filter(id=scheme_id).exists())

    def test_delete_nonexistent_scheme_returns_404(self):
        response = self.client.delete('/api/admin/schemes/99999/')
        self.assertEqual(response.status_code, 404)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=make_user(username="regular", email="regular@example.com"))
        response = self.client.get('/api/admin/schemes/')
        self.assertEqual(response.status_code, 403)

class AdminCriticalQuestionsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_admin()
        self.client.force_authenticate(user=self.admin)
        self.scheme = make_scheme(created_by=self.admin)

    def test_post_creates_critical_question(self):
        response = self.client.post('/api/admin/critical-questions/', {
            'question': 'Is this valid?',
            'scheme_id': self.scheme.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CriticalQuestion.objects.filter(question='Is this valid?').exists())

    def test_post_two_way_flag_is_set(self):
        self.client.post('/api/admin/critical-questions/', {
            'question': 'Two way?',
            'scheme_id': self.scheme.id,
            'two_way': True
        })
        cq = CriticalQuestion.objects.get(question='Two way?')
        self.assertTrue(cq.two_way)

    def test_post_missing_question_returns_400(self):
        response = self.client.post('/api/admin/critical-questions/', {
            'scheme_id': self.scheme.id
        })
        self.assertEqual(response.status_code, 400)

    def test_post_missing_scheme_id_returns_400(self):
        response = self.client.post('/api/admin/critical-questions/', {
            'question': 'Valid?'
        })
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_scheme_id_returns_404(self):
        response = self.client.post('/api/admin/critical-questions/', {
            'question': 'Valid?',
            'scheme_id': 99999
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_critical_question_returns_204(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question='To delete?')
        response = self.client.delete(f'/api/admin/critical-questions/{cq.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_removes_critical_question_from_db(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question='To delete 2?')
        cq_id = cq.id
        self.client.delete(f'/api/admin/critical-questions/{cq.id}/')
        self.assertFalse(CriticalQuestion.objects.filter(id=cq_id).exists())

    def test_delete_nonexistent_cq_returns_404(self):
        response = self.client.delete('/api/admin/critical-questions/99999/')
        self.assertEqual(response.status_code, 404)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=make_user(username="regular", email="regular@example.com"))
        response = self.client.post('/api/admin/critical-questions/', {
            'question': 'Valid?',
            'scheme_id': self.scheme.id
        })
        self.assertEqual(response.status_code, 403)