from backend.models import CriticalQuestion, ArgumentScheme


# -----------------------------
# Entry Point
# -----------------------------

def seed_critical_questions(test=False):
    print("Seeding Critical Questions", end="\r")

    generate_cq_fixtures()

    print("Critical Question seeding complete.")


# -----------------------------
# Fixtures
# -----------------------------

def generate_cq_fixtures():
    cq_map = {
        "Action": [
            "Does action A really achieve goal G?",
            "Could action A have negative consequences contrary to value V?",
            "Is scenario S correctly represented?",
        ],
        "Expert Opinion": [
            "Is expert E truly credible in domain S?",
            "Could expert E be biased?",
            "Is there conflicting evidence against claim X?",
        ],
        "Analogy": [
            "Are A and B really comparable?",
            "Does feature X of A necessarily apply to B?",
            "Could there be important differences between A and B?",
        ],
    }

    for scheme in ArgumentScheme.objects.all():
        questions = cq_map.get(
            scheme.name,
            ["Generic critical question"],
        )

        ensure_critical_questions(scheme, questions)


# -----------------------------
# Idempotent Sync
# -----------------------------

def ensure_critical_questions(scheme, questions):
    """
    Ensures all required critical questions exist.
    Safe to rerun indefinitely.
    """

    existing_questions = set(
        CriticalQuestion.objects.filter(scheme=scheme)
        .values_list("question", flat=True)
    )

    for question_text in questions:
        if question_text not in existing_questions:
            CriticalQuestion.objects.create(
                scheme=scheme,
                question=question_text,
            )