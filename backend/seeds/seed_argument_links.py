from backend.models import ArgumentLink, ArgumentScheme, CriticalQuestion
import random

NUM_LINKS = 40

schemes = list(ArgumentScheme.objects.all())
cqs = list(CriticalQuestion.objects.all())

def seed_argument_links(test=False):
    print("Seeding Argument Links", end="\r")
    generate_argument_links()
    print("Argument Link seeding complete.")

def generate_argument_links():
    if len(schemes) < 2 or not cqs:
        return

    created_links = 0
    while created_links < NUM_LINKS:
        parent = random.choice(schemes)
        child = random.choice([s for s in schemes if s != parent])
        cqs_for_parent = list(CriticalQuestion.objects.filter(scheme=parent))
        if not cqs_for_parent:
            continue
        cq = random.choice(cqs_for_parent)
        attacking = random.choice([True, False])

        try_create_argument_link(parent, child, cq, attacking)
        created_links += 1

def try_create_argument_link(parent, child, cq, attacking):
    if ArgumentLink.objects.filter(
        parent_argument=parent,
        child_argument=child,
        critical_question=cq,
        attacking=attacking
    ).exists():
        return
    link = ArgumentLink.objects.create(
        parent_argument=parent,
        child_argument=child,
        critical_question=cq,
        attacking=attacking
    )
    link.save()