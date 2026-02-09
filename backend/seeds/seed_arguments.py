from backend.models import User, ArgumentTheme, ArgumentScheme
import random
from faker import Faker

NUM_ARGUMENTS = 40
NUM_THEMES = 20
faker = Faker('en_GB')

def seed_arguments(test=False):
    print("Seeding Arguments",end='\r')
    generate_argument_fixtures()
    if not test:
        generate_random_arguments()
    print("Argument seeding complete.")

def generate_argument_fixtures():
    argument_fixtures = [
        {'author': 0, 'theme': 0, 'scheme': 0},
        {'author': 0, 'theme': 0, 'scheme': 0},
    ]
    for data in argument_fixtures:
        try_create_argument(data)

def generate_random_arguments():
    user_count = User.objects.count()
    while user_count < NUM_ARGUMENTS:
        generate_argument()
        user_count = User.objects.count()

def generate_argument():
    n_users = User.objects.count()
    author = random.randint(0, n_users-1)
    n_themes = ArgumentTheme.objects.count()
    theme = random.randint(0, n_themes-1)
    n_schemes = ArgumentScheme.objects.count()
    scheme = random.randint(0, n_schemes-1)

    try_create_argument({
        'author': author,
        'theme': theme,
        'scheme': scheme,
    })

def try_create_argument(data):
    try:
        Argument.objects.create(
            author = User.objects.all()[data['author']],
            theme = ArgumentTheme.objects.all()[data['theme']],
            scheme = ArgumentScheme.objects.all()[data['scheme']]
        )
    except:
        pass
