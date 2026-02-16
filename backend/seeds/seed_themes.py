from backend.models import ArgumentTheme, User
from faker import Faker

NUM_THEMES = 20
faker = Faker("en_GB")

users = list(User.objects.all())

def seed_argument_themes(test=False):
    print("Seeding Argument Themes", end="\r")
    generate_theme_fixtures()
    if not test:
        generate_random_themes()
    print("Argument Theme seeding complete.")

def generate_theme_fixtures():
    theme_fixtures = [
        {
            "title": "Other",
            "description": "Default theme for uncategorized arguments.",
            "creator": users[0] if len(users) > 0 else User.deleted_user(),
        },
        {
            "title": "Lockdown",
            "description": "Arguments related to lockdown policies and their impacts.",
            "creator": users[0] if len(users) > 0 else User.deleted_user(),
        },
        {
            "title": "Education",
            "description": "Arguments related to education policies and debates.",
            "creator": users[1] if len(users) > 1 else User.deleted_user(),
        },
    ]

    for data in theme_fixtures:
        try_create_theme(data)

def generate_random_themes():
    while ArgumentTheme.objects.count() < NUM_THEMES:
        generate_theme()

def generate_theme():
    title = faker.unique.word().capitalize()
    description = faker.sentence(nb_words=12)
    creator = random.choice(users) if users else User.deleted_user

    try_create_theme(
        {
            "title": title,
            "description": description,
            "creator": creator,
        }
    )

def try_create_theme(data):
    if ArgumentTheme.objects.filter(title=data["title"]).exists():
        return
    theme = ArgumentTheme.objects.create(
        title=data["title"],
        description=data.get("description", ""),
        creator=data.get("creator", random.choice(users)),
    )
    theme.save()