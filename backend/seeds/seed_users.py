from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from backend.models import User
import random
from faker import Faker

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
    user_fixtures = [
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
            "is_admin": False,
        },
        {
            "username": "janes2",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.org",
            "is_admin": False,
        },
    ]

    for data in user_fixtures:
        try_create_user(data)

def generate_random_users():
    while User.objects.count() < NUM_USERS:
        generate_user()

def generate_user():
    first_name = faker.first_name()
    last_name = faker.last_name()
    username = create_username(first_name, last_name)
    email = create_email(first_name, last_name)
    is_admin = random.choice([True, False])

    try_create_user(
        {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": is_admin,
        }
    )

def create_email(first_name, last_name):
    base_email = f"{first_name.lower()}.{last_name.lower()}@example.org"
    email = base_email
    counter = 1

    while User.objects.filter(email=email).exists():
        email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.org"
        counter += 1

    return email

def create_username(first_name, last_name):
    base_username = f"{first_name.lower()}.{last_name[0].lower()}"
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

def try_create_user(data):
    if User.objects.filter(username=data["username"]).exists():
        return
    user = User.objects.create(
        username=data["username"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        password=make_password(DEFAULT_PASSWORD),
        is_admin=data.get("is_admin", False),
        is_staff=data.get("is_admin", False),
        is_superuser=data.get("is_admin", False),
    )
    user.save()