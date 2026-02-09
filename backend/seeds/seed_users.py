from django.contrib.auth.hashers import make_password
from backend.models import User
import random
from faker import Faker

NUM_USERS = 100
DEFAULT_PASSWORD = "Password123"
faker = Faker('en_GB')

def seed_users(test=False):
    print("Seeding Users",end='\r')
    generate_user_fixtures()
    if not test:
        generate_random_users()
    print("User seeding complete.")

def generate_user_fixtures():
    user_fixtures = [
        {'username': 'johnd1', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.org', 'is_admin': True},
        {'username': 'janes2', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@example.org', 'is_admin': False},
    ]
    for data in user_fixtures:
        try_create_user(data)

def generate_random_users():
    user_count = User.objects.count()
    while user_count < NUM_USERS:
        generate_user()
        user_count = User.objects.count()

def generate_user():
    username = create_username(first_name, last_name)
    first_name = faker.first_name()
    last_name = faker.last_name()
    email = create_email(first_name, last_name)
    is_admin = random.choice([True, False])

    try_create_user({
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'is_admin': is_admin,
    })

def create_email(first_name, last_name):
    email = f"{first_name.lower()}.{last_name.lower()}@example.org"
    while User.objects.filter(email=email).exists():
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 1000)}@example.org"
    return email

def create_username(first_name, last_name):
    username = f"{first_name.lower()}.{last_name[0].lower()}"
    while User.objects.filter(username=username).exists():
        username = f"{first_name.lower()}.{last_name[0].lower()}{random.randint(1, 1000)}"
    return username

def try_create_user(data):
    try:
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=DEFAULT_PASSWORD,
            is_admin=data.get('is_admin', False),
        )
        user.password = make_password(DEFAULT_PASSWORD)
        user.save()
    except:
        pass