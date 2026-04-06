from django.contrib.auth.models import Group
from backend.models import User
from faker import Faker
import random

NUM_USERS = 100
DEFAULT_PASSWORD = "Password123"
faker = Faker("en_GB")

def seed_users(test=False):
    print("Seeding Users", end="\r")
    generate_user_fixtures()
    if not test:
        generate_random_users()
    print("User seeding complete.")


def generate_user_fixtures():
    fixtures = [
        {
            "username": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "email": "admin@example.org",
            "is_admin": True,
        },
        {
            "username": "johnd1",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.org",
        },
        {
            "username": "janes2",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.org",
        },
    ]
    for data in fixtures:
        try_create_user(data)

def generate_random_users():
    while (User.objects.count() < NUM_USERS):
        first_name = faker.first_name()
        last_name = faker.last_name()
        username = create_username(first_name, last_name)
        email = create_email(first_name, last_name)

        try_create_user({
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        })

def create_username(first, last):
    existing = set(User.objects.values_list("username", flat=True))
    base = f"{first.lower()}.{last[0].lower()}"
    username = base
    counter = 1
    while username in existing:
        username = f"{base}{counter}"
        counter += 1
    return username


def create_email(first, last):
    existing = set(User.objects.values_list("email", flat=True))
    base = f"{first.lower()}.{last.lower()}@example.org"
    email = base
    counter = 1
    while email in existing:
        email = f"{first.lower()}.{last.lower()}{counter}@example.org"
        counter += 1
    return email

def try_create_user(data):
    if User.objects.filter(username=data["username"]).exists():
        return
    user = User(
        username=data["username"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
    )
    user.set_password(DEFAULT_PASSWORD)
    user.save()