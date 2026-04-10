from backend.models import ThemeRequest, User
from faker import Faker
import random

faker = Faker("en_GB")
NUM_THEME_REQUESTS = 20

def get_users():
    return list(User.objects.all())

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def seed_theme_requests(test=False):
    print("Seeding Theme Requests", end="\r")
    if not test:
        generate_random_theme_requests()
    print("Theme Requests seeding complete.")

def generate_random_theme_requests():
    while (ThemeRequest.objects.count() < NUM_THEME_REQUESTS):
        requested_by = resolve_user(random.choice(get_users()) if get_users() else None)
        title = faker.word()
        description = faker.paragraph()
        reason = faker.sentence(nb_words=15)
        try_create_user({
            "requested_by": requested_by,
            "title": title,
            "description": description,
            "reason": reason
        })

def try_create_user(data):
    if ThemeRequest.objects.filter(title=data["title"]).exists():
        return
    ThemeRequest.objects.create(
        requested_by=resolve_user(data.get("requested_by")),
        title=data.get("title", ""),
        description=data.get("description", ""),
        reason=data.get("reason", ""),
    )