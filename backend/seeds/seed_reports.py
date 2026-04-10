from backend.models import Argument, User
from faker import Faker
import random

faker = Faker("en_GB")

def get_users():
    return list(User.objects.all())

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def seed_reports(test=False):
    print("Seeding Reports", end="\r")
    if not test:
        random_args = Argument.objects.order_by('?')[:20]
        for arg in random_args:
            try_create_report(arg)
    print("Reports seeding complete.")

def try_create_report(arg):
    number_of_reports = random.randint(0, 10)
    for _ in range(number_of_reports):
        user = resolve_user(random.choice(get_users()) if get_users() else None)
        arg.reported_by.add(user)