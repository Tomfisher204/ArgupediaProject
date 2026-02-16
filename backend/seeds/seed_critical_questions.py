from backend.models import CriticalQuestion, ArgumentScheme

def seed_critical_questions(test=False):
    print("Seeding Critical Questions", end="\r")
    generate_cq_fixtures()
    print("Critical Question seeding complete.")

def generate_cq_fixtures():
    schemes = list(ArgumentScheme.objects.all())
    cq_map = {
        "Action": [
            "Does action A really achieve goal G?",
            "Could action A have negative consequences contrary to value V?",
            "Is scenario S correctly represented?"
        ],
        "Expert Opinion": [
            "Is expert E truly credible in domain S?",
            "Could expert E be biased?",
            "Is there conflicting evidence against claim X?"
        ],
        "Analogy": [
            "Are A and B really comparable?",
            "Does feature X of A necessarily apply to B?",
            "Could there be important differences between A and B?"
        ]
    }
    for scheme in schemes:
        questions = cq_map.get(scheme.name, ["Generic critical question"])
        for question_text in questions:
            try_create_cq(scheme, question_text)

def try_create_cq(scheme, question_text):
    if CriticalQuestion.objects.filter(scheme=scheme, question=question_text).exists():
        return
    cq = CriticalQuestion.objects.create(
        scheme=scheme,
        question=question_text
    )
    cq.save()