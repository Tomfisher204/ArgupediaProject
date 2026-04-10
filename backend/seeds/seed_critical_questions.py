import random
from backend.models import CriticalQuestion, ArgumentScheme

def seed_critical_questions(test=False):
    print("Seeding Critical Questions", end="\r")
    generate_cq_fixtures()
    print("Critical Question seeding complete.")

def generate_cq_fixtures():
    cq_fixtures = {
        "Action": [
            ("Does action A really achieve goal G?", True),
            ("Could action A have negative consequences contrary to value V?", False),
            ("Is scenario S correctly represented?", False),
            ("Does action A conflict with other goals?", False),
        ],
        "Expert Opinion": [
            ("Is expert E truly credible in domain S?", True),
            ("Could expert E be biased?", False),
            ("Is there conflicting evidence against claim X?", False),
        ],
        "Analogy": [
            ("Are A and B really comparable?", True),
            ("Does feature X of A necessarily apply to B?", False),
            ("Could there be important differences between A and B?", False),
        ],
    }
    for scheme in ArgumentScheme.objects.all():
        fixture_questions = cq_fixtures.get(scheme.name)
        ensure_critical_questions(scheme, fixture_questions)

def ensure_critical_questions(scheme, questions):
    for question_text, two_way in questions:
        CriticalQuestion.objects.create(
            scheme=scheme,
            question=question_text,
            two_way=two_way,
        )