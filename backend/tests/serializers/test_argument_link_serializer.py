from django.test import TestCase
from backend.models import User, ArgumentScheme, ArgumentTheme, Argument, CriticalQuestion, ArgumentLink
from backend.serializers import ArgumentLinkSerializer

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

def make_argument(username, email, scheme, theme):
    return Argument.objects.create(
        author=make_user(username=username, email=email),
        scheme=scheme, theme=theme,
    )

def make_critical_question(scheme, question="Is this valid?", two_way=False):
    return CriticalQuestion.objects.create(scheme=scheme, question=question, two_way=two_way)

class ArgumentLinkSerializerTests(TestCase):
    """Tests for the ArgumentLinkSerializer."""

    def setUp(self):
        self.scheme = make_scheme()
        self.theme = make_theme()
        self.arg_a = make_argument("author_a", "author_a@example.com", self.scheme, self.theme)
        self.arg_b = make_argument("author_b", "author_b@example.com", self.scheme, self.theme)
        self.cq = make_critical_question(self.scheme)
        self.link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.cq,
            attacking=True,
        )

    def test_contains_expected_fields(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertEqual(set(serializer.data.keys()), {'id', 'parent_argument', 'child_argument', 'critical_question', 'attacking', 'date_created'})

    def test_parent_argument_value(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertEqual(serializer.data['parent_argument'], self.arg_a.id)

    def test_child_argument_value(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertEqual(serializer.data['child_argument'], self.arg_b.id)

    def test_critical_question_value(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertEqual(serializer.data['critical_question'], self.cq.id)

    def test_attacking_value(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertTrue(serializer.data['attacking'])

    def test_date_created_present(self):
        serializer = ArgumentLinkSerializer(self.link)
        self.assertIsNotNone(serializer.data['date_created'])