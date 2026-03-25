from django.contrib.auth.models import Group
from backend.models import User
from faker import Faker
import random

NUM_USERS = 100
DEFAULT_PASSWORD = "Password123"
faker = Faker("en_GB")


# -----------------------------
# Entry Point
# -----------------------------

def seed_users(test=False):
    print("Seeding Users", end="\r")

    generate_user_fixtures()

    if not test:
        generate_random_users()

    print("User seeding complete.")


# -----------------------------
# Fixtures
# -----------------------------

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


# -----------------------------
# Random Users
# -----------------------------

def generate_random_users():
    existing_usernames = set(
        User.objects.values_list("username", flat=True)
    )
    existing_emails = set(
        User.objects.values_list("email", flat=True)
    )

    attempts = 0
    max_attempts = NUM_USERS * 5  # prevents infinite loop

    while (
        User.objects.count() < NUM_USERS
        and attempts < max_attempts
    ):
        attempts += 1

        first = faker.first_name()
        last = faker.last_name()

        username = create_username(first, last, existing_usernames)
        email = create_email(first, last, existing_emails)

        try_create_user({
            "username": username,
            "email": email,
            "first_name": first,
            "last_name": last,
            "is_admin": random.choice([True, False]),
        })

        existing_usernames.add(username)
        existing_emails.add(email)


# -----------------------------
# Generators (NO DB QUERIES)
# -----------------------------

def create_username(first, last, existing):
    base = f"{first.lower()}.{last[0].lower()}"
    username = base
    counter = 1

    while username in existing:
        username = f"{base}{counter}"
        counter += 1

    return username


def create_email(first, last, existing):
    base = f"{first.lower()}.{last.lower()}@example.org"
    email = base
    counter = 1

    while email in existing:
        email = f"{first.lower()}.{last.lower()}{counter}@example.org"
        counter += 1

    return email


# -----------------------------
# Creation Logic
# -----------------------------

def try_create_user(data):
    if User.objects.filter(username=data["username"]).exists():
        return

    is_admin = data.get("is_admin", False)

    user = User(
        username=data["username"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        is_staff=is_admin,
        is_superuser=is_admin,
        is_admin=is_admin,
    )

    user.set_password(DEFAULT_PASSWORD)
    user.save()