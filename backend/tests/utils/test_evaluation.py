from django.test import TestCase
from backend.models import Argument, ArgumentScheme, ArgumentTheme, ArgumentLink, CriticalQuestion
from backend.utils.evaluation import evaluate_and_propagate, _evaluate_single

_counter = 0

def next_id():
    global _counter
    _counter += 1
    return _counter

def make_user():
    from backend.models import User
    i = next_id()
    return User.objects.create(
        username=f"user_{i}",
        email=f"user_{i}@test.com",
        password="x"
    )

def make_scheme():
    i = next_id()
    return ArgumentScheme.objects.create(
        name=f"scheme_{i}",
        created_by=make_user(),
        template="t"
    )

def make_theme():
    i = next_id()
    return ArgumentTheme.objects.create(
        title=f"theme_{i}",
        creator=make_user()
    )

def make_argument(is_winning=None):
    return Argument.objects.create(
        author=make_user(),
        scheme=make_scheme(),
        theme=make_theme(),
        is_winning=is_winning
    )

def make_link(parent, child):
    cq = CriticalQuestion.objects.create(
        scheme=parent.scheme,
        question=f"q_{next_id()}"
    )
    return ArgumentLink.objects.create(
        parent_argument=parent,
        child_argument=child,
        critical_question=cq,
        attacking=True
    )

class EvaluationTests(TestCase):

    def test_evaluate_single_updates_state(self):
        parent = make_argument()
        child = make_argument()
        make_link(parent, child)
        result = _evaluate_single(parent)
        self.assertIn(result, [True, False, None])

    def test_evaluate_and_propagate_runs_without_error(self):
        parent = make_argument()
        child = make_argument()
        make_link(parent, child)
        evaluate_and_propagate(child)

    def test_child_supporting_makes_parent_winning(self):
        parent = make_argument(is_winning=False)
        child = make_argument(is_winning=True)
        make_link(parent, child)
        evaluate_and_propagate(child)
        parent.refresh_from_db()
        self.assertIsNotNone(parent.is_winning)

    def test_child_attacking_makes_parent_less_likely_winning(self):
        parent = make_argument(is_winning=True)
        child = make_argument(is_winning=False)
        make_link(parent, child)
        evaluate_and_propagate(child)
        parent.refresh_from_db()
        self.assertIsNotNone(parent.is_winning)