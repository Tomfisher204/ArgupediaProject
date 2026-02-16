from backend.models import ArgumentScheme, SchemeField, User

users = list(User.objects.all())

def seed_argument_schemes(test=False):
    print("Seeding Argument Schemes", end="\r")
    generate_scheme_fixtures()
    print("Argument Scheme seeding complete.")

def generate_scheme_fixtures():
    scheme_fixtures = [
        {
            "name": "Action",
            "description": "In scenario S, action A achieves G and promotes value V.",
            "created_by": users[0] if len(users) > 0 else User.deleted_user(),
            "fields": ["Scenario (S)", "Action (A)", "Goal (G)", "Value (V)"]
        },
        {
            "name": "Expert Opinion",
            "description": "Expert E in domain D says C.",
            "created_by": users[0] if len(users) > 0 else User.deleted_user(),
            "fields": ["Expert (E)", "Domain (D)", "Claim (C)"]
        },
        {
            "name": "Analogy",
            "description": "A and B are similar; if A has feature X, so will B.",
            "created_by": users[0] if len(users) > 0 else User.deleted_user(),
            "fields": ["Item A", "Item B", "Feature X"]
        },
    ]

    for data in scheme_fixtures:
        try_create_scheme(data)

def try_create_scheme(data):
    if ArgumentScheme.objects.filter(name=data["name"]).exists():
        return
    scheme = ArgumentScheme.objects.create(
        name=data["name"],
        description=data.get("description", ""),
        created_by=data.get("created_by", User.deleted_user),
    )
    scheme.save()

    for field_name in data.get("fields", []):
        field = SchemeField.objects.create(
            scheme=scheme,
            name=field_name
        )
        field.save()