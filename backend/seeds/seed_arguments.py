from backend.models import Argument, ArgmentFieldValue, User, ArgumentTheme, ArgumentScheme
from faker import Faker
import random

NUM_ARGUMENTS = 120
faker = Faker("en_GB")

def get_users():
    return list(User.objects.all())

def get_themes():
    themes = list(ArgumentTheme.objects.all())
    if not themes:
        themes = [ArgumentTheme.get_or_create_other_theme()]
    return themes

def get_schemes():
    return list(
        ArgumentScheme.objects.prefetch_related("fields")
    )

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def seed_arguments(test=False):
    print("Seeding Arguments", end="\r")
    generate_argument_fixtures()
    if not test:
        generate_random_arguments()
    print("Argument seeding complete.")

def generate_argument_fixtures():
    users = get_users()
    themes = get_themes()
    schemes = get_schemes()
    if not schemes:
        return
    fixtures = [
        {
            "author": users[1] if len(users) > 1 else None,
            "theme": themes[0],
            "scheme": schemes[0],
        },
        {
            "author": users[1] if len(users) > 1 else None,
            "theme": themes[min(1, len(themes)-1)],
            "scheme": schemes[min(1, len(schemes)-1)],
        },
        {
            "author": users[2] if len(users) > 2 else None,
            "theme": themes[min(2, len(themes)-1)],
            "scheme": schemes[min(2, len(schemes)-1)],
        },
    ]
    for data in fixtures:
        try_create_argument(data)

def generate_random_arguments():
    users = get_users()
    themes = get_themes()
    schemes = get_schemes()
    if not schemes:
        return
    attempts = 0
    max_attempts = NUM_ARGUMENTS*5
    while (
        Argument.objects.count() < NUM_ARGUMENTS
        and attempts < max_attempts
    ):
        attempts += 1
        try_create_argument({
            "author": random.choice(users) if users else None,
            "theme": random.choice(themes),
            "scheme": random.choice(schemes),
        })

def try_create_argument(data):
    scheme = data["scheme"]
    argument = Argument.objects.create(
        author=resolve_user(data.get("author")),
        theme=data.get("theme")
        or ArgumentTheme.get_or_create_other_theme(),
        scheme=scheme,
    )
    field_values = [
        ArgumentFieldValue(
            argument = argument,
            scheme_field = field,
            value = " ".join(faker.words(nb=random.randint(1, 4)))
        )
        for field in scheme.fields.all()
    ]
    ArgumentFieldValue.objects.bulk_create(field_values)