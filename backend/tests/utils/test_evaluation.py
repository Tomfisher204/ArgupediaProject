from django.test import TestCase
from backend.models import Argument, ArgumentScheme, ArgumentTheme, ArgumentLink, CriticalQuestion, User
from backend.utils.evaluation import evaluate_and_propagate, _evaluate_single, _compute_is_winning


def make_user(username="eval_user", email="eval@test.com", password="Password123"):
    return User.objects.create(username=username, email=email, password=password)

def make_scheme(name="eval_scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username="scheme_user", email="scheme@test.com"),
        template="t",
    )

def make_theme(title="eval_theme", creator=None):
    return ArgumentTheme.objects.create(
        title=title,
        creator=creator or make_user(username="theme_user", email="theme@test.com"),
    )

def make_argument(author, scheme, theme, is_winning=None):
    return Argument.objects.create(author=author, scheme=scheme, theme=theme, is_winning=is_winning)

def make_link(parent, child, attacking=True):
    cq = CriticalQuestion.objects.create(scheme=parent.scheme, question="Is this valid?")
    return ArgumentLink.objects.create(parent_argument=parent, child_argument=child, critical_question=cq, attacking=attacking)


class EvaluationTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def make_arg(self, is_winning=None):
        return make_argument(self.user, self.scheme, self.theme, is_winning=is_winning)

    def test_no_children_returns_true(self):
        parent = self.make_arg()
        result = _compute_is_winning(parent)
        self.assertTrue(result)

    def test_winning_support_makes_parent_winning(self):
        parent = self.make_arg()
        for _ in range(5):
            child = self.make_arg(is_winning=True)
            make_link(parent, child, attacking=False)
        result = _compute_is_winning(parent)
        self.assertTrue(result)

    def test_winning_attack_makes_parent_losing(self):
        parent = self.make_arg()
        for _ in range(5):
            child = self.make_arg(is_winning=True)
            make_link(parent, child, attacking=True)
        result = _compute_is_winning(parent)
        self.assertFalse(result)

    def test_balanced_children_returns_none(self):
        parent = self.make_arg()
        make_link(parent, self.make_arg(is_winning=True), attacking=False)
        make_link(parent, self.make_arg(is_winning=True), attacking=True)
        result = _compute_is_winning(parent)
        self.assertIsNone(result)

    def test_evaluate_single_no_change_returns_false(self):
        parent = self.make_arg(is_winning=True)
        result = _evaluate_single(parent)
        self.assertFalse(result)

    def test_evaluate_single_changed_returns_true(self):
        parent = self.make_arg(is_winning=False)
        result = _evaluate_single(parent)
        self.assertTrue(result)

    def test_propagate_stops_when_no_change(self):
        parent = self.make_arg(is_winning=True)
        child = self.make_arg(is_winning=True)
        make_link(parent, child, attacking=False)
        evaluate_and_propagate(child)
        parent.refresh_from_db()
        self.assertIsNotNone(parent.is_winning)

    def test_propagate_updates_grandparent(self):
        grandparent = self.make_arg(is_winning=False)
        parent = self.make_arg(is_winning=False)
        child = self.make_arg(is_winning=True)
        make_link(grandparent, parent, attacking=False)
        make_link(parent, child, attacking=False)
        evaluate_and_propagate(child)
        grandparent.refresh_from_db()
        self.assertIsNotNone(grandparent.is_winning)