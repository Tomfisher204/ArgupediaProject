from backend.models import Argument, ArgumentFieldValue, ArgumentVotes, User, ArgumentTheme, ArgumentScheme, SchemeField
from faker import Faker
import random

NUM_ARGUMENTS = 120
MAX_VOTES_PER_ARGUMENT = 5
faker = Faker("en_GB")

users = list(User.objects.all())
themes = list(ArgumentTheme.objects.all())
schemes = list(ArgumentScheme.objects.all())

def seed_arguments(test=False):
    print("Seeding Arguments", end="\r")
    generate_argument_fixtures()
    if not test:
        generate_random_arguments()
    print("Argument seeding complete.")

def generate_argument_fixtures():
    themes = list(ArgumentTheme.objects.all())
    schemes = list(ArgumentScheme.objects.all())

    argument_fixtures = [
        {
            "author": users[1] if len(users) > 1 else User.deleted_user(),
            "theme": themes[0] if len(themes) > 0 else ArgumentTheme.get_or_create_other_theme(),
            "scheme": schemes[0] if len(schemes) > 0 else None,
        },
        {
            "author": users[1] if len(users) > 1 else User.deleted_user(),
            "theme": themes[1] if len(themes) > 1 else ArgumentTheme.get_or_create_other_theme(),
            "scheme": schemes[1] if len(schemes) > 1 else None,
        },
        {
            "author": users[2] if len(users) > 2 else User.deleted_user(),
            "theme": themes[2] if len(themes) > 2 else ArgumentTheme.get_or_create_other_theme(),
            "scheme": schemes[2] if len(schemes) > 2 else None,
        },
    ]

    for data in argument_fixtures:
        try_create_argument(data)

def generate_random_arguments():
    while Argument.objects.count() < NUM_ARGUMENTS:
        author = random.choice(users) if users else User.deleted_user()
        theme = random.choice(themes) if themes else ArgumentTheme.get_or_create_other_theme()
        scheme = random.choice(schemes) if schemes else None
        if not scheme:
            continue

        try_create_argument({
            "author": author,
            "theme": theme,
            "scheme": scheme,
        })

def try_create_argument(data):
    argument = Argument.objects.create(
        author=data.get("author", User.deleted_user),
        theme=data.get("theme", ArgumentTheme.get_or_create_other_theme()),
        scheme=data["scheme"],
    )
    argument.save()

    for field in data["scheme"].fields.all():
        value = faker.sentence(nb_words=6)
        field_value = ArgumentFieldValue.objects.create(
            argument=argument,
            scheme_field=field,
            value=value
        )
        field_value.save()

    num_votes = random.randint(0, min(len(users), MAX_VOTES_PER_ARGUMENT))
    voters = random.sample(users, num_votes) if users else []
    for user in voters:
        is_upvote = random.choice([True, False])
        vote = ArgumentVotes.objects.create(
            argument=argument,
            user=user,
            is_upvote=is_upvote
        )
        vote.save()