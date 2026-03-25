from backend.models import ArgumentScheme, SchemeField, User


# -----------------------------
# Helpers (STANDARD PATTERN)
# -----------------------------

def get_users():
    return list(User.objects.all())


def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()


# -----------------------------
# Entry Point
# -----------------------------

def seed_argument_schemes(test=False):
    print("Seeding Argument Schemes", end="\r")

    generate_scheme_fixtures()

    print("Argument Scheme seeding complete.")


# -----------------------------
# Fixtures
# -----------------------------

def generate_scheme_fixtures():
    users = get_users()
    deleted = User.deleted_user()

    scheme_fixtures = [
        {
            "name": "Action",
            "description": "In scenario S, action A achieves G and promotes value V.",
            "created_by": users[0] if users else deleted,
            "fields": ["Scenario (S)", "Action (A)", "Goal (G)", "Value (V)"],
        },
        {
            "name": "Expert Opinion",
            "description": "Expert E in domain D says C.",
            "created_by": users[0] if users else deleted,
            "fields": ["Expert (E)", "Domain (D)", "Claim (C)"],
        },
        {
            "name": "Analogy",
            "description": "A and B are similar; if A has feature X, so will B.",
            "created_by": users[0] if users else deleted,
            "fields": ["Item A", "Item B", "Feature X"],
        },
    ]

    for data in scheme_fixtures:
        try_create_scheme(data)


# -----------------------------
# Creation Logic
# -----------------------------

def try_create_scheme(data):
    scheme, created = ArgumentScheme.objects.get_or_create(
        name=data["name"],
        defaults={
            "description": data.get("description", ""),
            "created_by": resolve_user(data.get("created_by")),
        },
    )

    # Optional: update description if reseeding
    if not created:
        scheme.description = data.get("description", "")
        scheme.save(update_fields=["description"])

    ensure_scheme_fields(scheme, data.get("fields", []))


# -----------------------------
# Field Sync (IDEMPOTENT)
# -----------------------------

def ensure_scheme_fields(scheme, field_names):
    """
    Ensures scheme has exactly the required fields.
    Safe to rerun repeatedly.
    """

    existing_fields = {
        f.name: f for f in SchemeField.objects.filter(scheme=scheme)
    }

    for name in field_names:
        if name not in existing_fields:
            SchemeField.objects.create(
                scheme=scheme,
                name=name,
            )