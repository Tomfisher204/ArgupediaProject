from backend.models import ArgumentScheme, SchemeField, User

def get_users():
    return list(User.objects.all())

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def seed_argument_schemes(test=False):
    print("Seeding Argument Schemes", end="\r")
    generate_scheme_fixtures()
    print("Argument Scheme seeding complete.")

def generate_scheme_fixtures():
    users = get_users()
    deleted = User.deleted_user()

    scheme_fixtures = [
        {
            "name": "Action",
            "description": "In scenario S, action A achieves G and promotes value V.",
            "template": "In **Scenario (S)**, **Action (A)** achieves **Goal (G)** and promotes **Value (V)**.",
            "created_by": users[0] if users else deleted,
            "fields": ["Scenario (S)", "Action (A)", "Goal (G)", "Value (V)"],
        },
        {
            "name": "Expert Opinion",
            "description": "Expert E in domain D says C.",
            "template": "Expert **Expert (E)** in domain **Domain (D)** says **Claim (C)**.",
            "created_by": users[0] if users else deleted,
            "fields": ["Expert (E)", "Domain (D)", "Claim (C)"],
        },
        {
            "name": "Analogy",
            "description": "A and B are similar; if A has feature X, so will B.",
            "template": "**Item A** and **Item B** are similar; if **Item A** has **Feature X**, so will **Item B**.",
            "created_by": users[0] if users else deleted,
            "fields": ["Item A", "Item B", "Feature X"],
        },
    ]
    for data in scheme_fixtures:
        try_create_scheme(data)

def try_create_scheme(data):
    scheme, created = ArgumentScheme.objects.get_or_create(
        name=data["name"],
        defaults={
            "description": data.get("description", ""),
            "template": data.get("template", ""),
            "created_by": resolve_user(data.get("created_by")),
        },
    )
    if not created:
        scheme.description = data.get("description", "")
        scheme.template = data.get("template", "")
        scheme.save(update_fields=["description", "template"])
    ensure_scheme_fields(scheme, data.get("fields", []))

def ensure_scheme_fields(scheme, field_names):
    existing_fields = {
        f.name: f for f in SchemeField.objects.filter(scheme=scheme)
    }
    for name in field_names:
        if name not in existing_fields:
            SchemeField.objects.create(
                scheme=scheme,
                name=name,
            )