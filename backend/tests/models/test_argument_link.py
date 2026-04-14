from django.test import TestCase
from django.utils import timezone
from backend.models import User, ArgumentScheme, ArgumentTheme, Argument, CriticalQuestion, ArgumentLink

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

def make_scheme(name="Test Scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username=f"scheme_creator_{name}", email=f"sc_{name}@example.com"),
    )

def make_theme(title="Science", creator=None):
    return ArgumentTheme.objects.create(
        title=title,
        creator=creator or make_user(username=f"theme_creator_{title}", email=f"tc_{title}@example.com"),
    )

def make_argument(username, email, scheme, theme):
    return Argument.objects.create(
        author=make_user(username=username, email=email),
        scheme=scheme,
        theme=theme,
    )

class ArgumentLinkModelTests(TestCase):
    """Tests for the ArgumentLink model validation and functionality."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.arg_a = make_argument("author_a", "author_a@example.com", self.scheme, self.theme)
        self.arg_b = make_argument("author_b", "author_b@example.com", self.scheme, self.theme)
        self.one_way_cq = CriticalQuestion.objects.create(scheme=self.scheme, question="One-way CQ?", two_way=False)
        self.two_way_cq = CriticalQuestion.objects.create(scheme=self.scheme, question="Two-way CQ?", two_way=True)

    def test_create_argument_link(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        self.assertEqual(link.parent_argument, self.arg_a)
        self.assertEqual(link.child_argument, self.arg_b)
        self.assertEqual(link.critical_question, self.one_way_cq)

    def test_attacking_defaults_to_true(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        self.assertTrue(link.attacking)

    def test_attacking_can_be_set_false(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
            attacking=False,
        )
        self.assertFalse(link.attacking)

    def test_date_created_auto_set(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        self.assertIsNotNone(link.date_created)
        self.assertLessEqual(link.date_created, timezone.now())

    def test_one_way_cq_does_not_create_reciprocal(self):
        ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        self.assertEqual(ArgumentLink.objects.count(), 1)

    def test_two_way_cq_creates_reciprocal_link(self):
        ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.two_way_cq,
        )
        self.assertEqual(ArgumentLink.objects.count(), 2)
        reciprocal_exists = ArgumentLink.objects.filter(
            parent_argument=self.arg_b,
            child_argument=self.arg_a,
            critical_question=self.two_way_cq,
        ).exists()
        self.assertTrue(reciprocal_exists)

    def test_two_way_reciprocal_not_duplicated_on_resave(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.two_way_cq,
        )
        link.save()
        self.assertEqual(ArgumentLink.objects.count(), 2)

    def test_two_way_reciprocal_preserves_attacking_flag(self):
        ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.two_way_cq,
            attacking=False,
        )
        reciprocal = ArgumentLink.objects.get(
            parent_argument=self.arg_b,
            child_argument=self.arg_a,
        )
        self.assertFalse(reciprocal.attacking)

    def test_cascade_delete_with_parent_argument(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        link_id = link.id
        self.arg_a.delete()
        self.assertFalse(ArgumentLink.objects.filter(id=link_id).exists())

    def test_cascade_delete_with_critical_question(self):
        link = ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        link_id = link.id
        self.one_way_cq.delete()
        self.assertFalse(ArgumentLink.objects.filter(id=link_id).exists())

    def test_related_names_child_and_parent_links(self):
        ArgumentLink.objects.create(
            parent_argument=self.arg_a,
            child_argument=self.arg_b,
            critical_question=self.one_way_cq,
        )
        self.assertEqual(self.arg_a.child_links.count(), 1)
        self.assertEqual(self.arg_b.parent_links.count(), 1)