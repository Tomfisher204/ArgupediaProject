from django.test import TestCase
from unittest.mock import MagicMock
from django.contrib.auth.models import AnonymousUser
from backend.models import User, ArgumentScheme, ArgumentTheme, SchemeField, Argument, ArgumentFieldValue, CriticalQuestion, ArgumentLink
from backend.serializers import FieldValueSerializer, ArgumentSummarySerializer, ChildArgumentSerializer, ArgumentDetailSerializer, CreateArgumentSerializer

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

def make_argument(author, scheme, theme, **kwargs):
    return Argument.objects.create(author=author, scheme=scheme, theme=theme, **kwargs)

def make_mock_request(user=None, authenticated=True):
    mock_request = MagicMock()
    mock_request.user = user if authenticated else AnonymousUser()
    return mock_request

class FieldValueSerializerTests(TestCase):
    """Tests for the FieldValueSerializer."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = make_argument(self.user, self.scheme, self.theme)
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        self.afv = ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value="All men are mortal.")

    def test_contains_expected_fields(self):
        serializer = FieldValueSerializer(self.afv)
        self.assertEqual(set(serializer.data.keys()), {'field_name', 'value'})

    def test_field_name_value(self):
        serializer = FieldValueSerializer(self.afv)
        self.assertEqual(serializer.data['field_name'], "Premise")

    def test_value_value(self):
        serializer = FieldValueSerializer(self.afv)
        self.assertEqual(serializer.data['value'], "All men are mortal.")

class ArgumentSummarySerializerTests(TestCase):
    """Tests for the ArgumentSummarySerializer."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = make_argument(self.user, self.scheme, self.theme)

    def test_contains_expected_fields(self):
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(set(serializer.data.keys()), {'id', 'author', 'theme', 'scheme_name', 'scheme_template', 'field_values', 'date_created', 'child_count', 'is_winning'})

    def test_author_is_username(self):
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(serializer.data['author'], self.user.username)

    def test_theme_is_title(self):
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(serializer.data['theme'], self.theme.title)

    def test_scheme_name_value(self):
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(serializer.data['scheme_name'], self.scheme.name)

    def test_child_count_zero_with_no_links(self):
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(serializer.data['child_count'], 0)

    def test_child_count_with_links(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")
        child = make_argument(make_user(username="child_author", email="child@example.com"), self.scheme, self.theme)
        ArgumentLink.objects.create(parent_argument=self.argument, child_argument=child, critical_question=cq)
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(serializer.data['child_count'], 1)

    def test_field_values_nested(self):
        field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=field, value="Test value")
        serializer = ArgumentSummarySerializer(self.argument)
        self.assertEqual(len(serializer.data['field_values']), 1)
        self.assertEqual(serializer.data['field_values'][0]['field_name'], "Premise")

class ArgumentDetailSerializerTests(TestCase):
    """Tests for the ArgumentDetailSerializer."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = make_argument(self.user, self.scheme, self.theme)
        self.cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")

    def test_contains_expected_fields(self):
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertEqual(set(serializer.data.keys()), {'id', 'author', 'theme', 'theme_id', 'scheme_name', 'scheme_id', 'scheme_template', 'field_values', 'date_created', 'attackers', 'supporters', 'reported', 'report_count', 'is_winning'})

    def test_attackers_only_contains_attacking_links(self):
        child = make_argument(make_user(username="child_a", email="child_a@example.com"), self.scheme, self.theme)
        ArgumentLink.objects.create(parent_argument=self.argument, child_argument=child, critical_question=self.cq, attacking=True)
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertEqual(len(serializer.data['attackers']), 1)
        self.assertEqual(len(serializer.data['supporters']), 0)

    def test_supporters_only_contains_supporting_links(self):
        child = make_argument(make_user(username="child_s", email="child_s@example.com"), self.scheme, self.theme)
        ArgumentLink.objects.create(parent_argument=self.argument, child_argument=child, critical_question=self.cq, attacking=False)
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertEqual(len(serializer.data['supporters']), 1)
        self.assertEqual(len(serializer.data['attackers']), 0)

    def test_reported_true_when_user_has_reported(self):
        self.argument.reported_by.add(self.user)
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.data['reported'])

    def test_reported_false_when_user_has_not_reported(self):
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.data['reported'])

    def test_reported_false_when_unauthenticated(self):
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user, authenticated=False)})
        self.assertFalse(serializer.data['reported'])

    def test_report_count(self):
        reporter = make_user(username="reporter", email="reporter@example.com")
        self.argument.reported_by.add(reporter)
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertEqual(serializer.data['report_count'], 1)

    def test_theme_id_and_scheme_id_values(self):
        serializer = ArgumentDetailSerializer(self.argument, context={'request': make_mock_request(self.user)})
        self.assertEqual(serializer.data['theme_id'], self.theme.id)
        self.assertEqual(serializer.data['scheme_id'], self.scheme.id)

class CreateArgumentSerializerTests(TestCase):
    """Tests for the CreateArgumentSerializer validation and creation logic."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)
        self.valid_data = {
            'scheme_id': self.scheme.id,
            'theme_id': self.theme.id,
            'field_values': [{'scheme_field_id': self.field.id, 'value': 'Test premise'}],
        }

    def test_valid_data_is_valid(self):
        serializer = CreateArgumentSerializer(data=self.valid_data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())

    def test_create_argument(self):
        serializer = CreateArgumentSerializer(data=self.valid_data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        argument = serializer.save()
        self.assertIsInstance(argument, Argument)
        self.assertEqual(argument.author, self.user)

    def test_create_argument_creates_field_values(self):
        serializer = CreateArgumentSerializer(data=self.valid_data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        argument = serializer.save()
        self.assertEqual(argument.field_values.count(), 1)
        self.assertEqual(argument.field_values.first().value, 'Test premise')

    def test_parent_without_critical_question_is_invalid(self):
        parent = make_argument(self.user, self.scheme, self.theme)
        data = self.valid_data.copy()
        data['parent_argument_id'] = parent.id
        serializer = CreateArgumentSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('critical_question_id', serializer.errors)

    def test_critical_question_without_parent_is_invalid(self):
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")
        data = self.valid_data.copy()
        data['critical_question_id'] = cq.id
        serializer = CreateArgumentSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent_argument_id', serializer.errors)

    def test_valid_parent_and_critical_question_creates_link(self):
        parent = make_argument(make_user(username="parent_author", email="parent@example.com"), self.scheme, self.theme)
        cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Valid?")
        data = self.valid_data.copy()
        data['parent_argument_id'] = parent.id
        data['critical_question_id'] = cq.id
        serializer = CreateArgumentSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        argument = serializer.save()
        self.assertTrue(ArgumentLink.objects.filter(parent_argument=parent, child_argument=argument).exists())

    def test_field_id_not_in_scheme_is_invalid(self):
        other_scheme = make_scheme(name="Other Scheme", created_by=self.user)
        other_field = SchemeField.objects.create(scheme=other_scheme, name="Other Field", order=1)
        data = self.valid_data.copy()
        data['field_values'] = [{'scheme_field_id': other_field.id, 'value': 'Wrong field'}]
        serializer = CreateArgumentSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('field_values', serializer.errors)

    def test_root_flag_is_set_on_argument(self):
        data = self.valid_data.copy()
        data['root'] = True
        serializer = CreateArgumentSerializer(data=data, context={'request': make_mock_request(self.user)})
        self.assertTrue(serializer.is_valid())
        argument = serializer.save()
        self.assertTrue(argument.root)