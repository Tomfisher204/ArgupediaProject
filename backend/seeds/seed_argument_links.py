from backend.models import ArgumentLink, Argument, CriticalQuestion
import random

NUM_LINKS = 40


# -----------------------------
# Entry Point
# -----------------------------

def seed_argument_links(test=False):
    print("Seeding Argument Links", end="\r")

    generate_argument_links()

    print("Argument Link seeding complete.")


# -----------------------------
# Link Generation
# -----------------------------

def generate_argument_links():
    arguments = list(Argument.objects.select_related("scheme"))
    if len(arguments) < 2:
        return

    # Map scheme -> critical questions (ONE QUERY)
    cq_map = build_cq_map()

    if not cq_map:
        return

    # Track existing links in memory
    existing_links = set(
        ArgumentLink.objects.values_list(
            "parent_argument_id",
            "child_argument_id",
            "critical_question_id",
            "attacking",
        )
    )

    created_links = 0
    attempts = 0
    max_attempts = NUM_LINKS * 10  # prevents infinite loops

    while created_links < NUM_LINKS and attempts < max_attempts:
        attempts += 1

        parent = random.choice(arguments)

        # choose different child efficiently
        child = random.choice(arguments)
        if child.id == parent.id:
            continue

        cqs_for_parent = cq_map.get(parent.scheme_id)
        if not cqs_for_parent:
            continue

        cq = random.choice(cqs_for_parent)
        attacking = random.choice([True, False])

        key = (parent.id, child.id, cq.id, attacking)

        if key in existing_links:
            continue

        ArgumentLink.objects.create(
            parent_argument=parent,
            child_argument=child,
            critical_question=cq,
            attacking=attacking,
        )

        existing_links.add(key)
        created_links += 1


# -----------------------------
# Helpers
# -----------------------------

def build_cq_map():
    """
    Returns:
        { scheme_id: [CriticalQuestion, ...] }
    """

    cq_map = {}

    for cq in CriticalQuestion.objects.select_related("scheme"):
        cq_map.setdefault(cq.scheme_id, []).append(cq)

    return cq_map