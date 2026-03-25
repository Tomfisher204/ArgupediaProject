from backend.models import ArgumentTheme, User
from faker import Faker
import random

NUM_THEMES = 20
faker = Faker("en_GB")


# -----------------------------
# Helpers (REUSABLE STANDARD)
# -----------------------------

def get_users():
    """Always fetch fresh users at runtime."""
    return list(User.objects.all())


def resolve_user(user):
    """
    Guarantees a valid User instance for FK assignment.
    """
    if isinstance(user, User):
        return user
    return User.deleted_user()


# -----------------------------
# Public Seeder Entry
# -----------------------------

def seed_argument_themes(test=False):
    print("Seeding Argument Themes", end="\r")

    generate_theme_fixtures()

    if not test:
        generate_random_themes()

    print("Argument Theme seeding complete.")


# -----------------------------
# Fixtures
# -----------------------------

def generate_theme_fixtures():
    users = get_users()
    deleted = User.deleted_user()

    theme_fixtures = [
        {
            "title": "Other",
            "description": "Default theme for uncategorized arguments.",
            "creator": users[0] if len(users) > 0 else deleted,
        },
        {
            "title": "Lockdown",
            "description": "Arguments related to lockdown policies and their impacts.",
            "creator": users[0] if len(users) > 0 else deleted,
        },
        {
            "title": "Education",
            "description": "Arguments related to education policies and debates.",
            "creator": users[1] if len(users) > 1 else deleted,
        },
    ]

    for data in theme_fixtures:
        try_create_theme(data)


# -----------------------------
# Random Generation
# -----------------------------

def generate_random_themes():
    users = get_users()
    deleted = User.deleted_user()

    attempts = 0
    max_attempts = NUM_THEMES * 5  # prevents infinite loops

    while (
        ArgumentTheme.objects.count() < NUM_THEMES
        and attempts < max_attempts
    ):
        attempts += 1

        title = faker.unique.word().capitalize()
        description = faker.sentence(nb_words=12)
        creator = random.choice(users) if users else deleted

        try_create_theme({
            "title": title,
            "description": description,
            "creator": creator,
        })


# -----------------------------
# Creation Logic
# -----------------------------

def try_create_theme(data):
    title = data["title"]

    # idempotency (safe re-seeding)
    if ArgumentTheme.objects.filter(title=title).exists():
        return

    ArgumentTheme.objects.create(
        title=title,
        description=data.get("description", ""),
        creator=resolve_user(data.get("creator")),
    )