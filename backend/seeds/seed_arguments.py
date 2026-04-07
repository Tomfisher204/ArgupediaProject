import random
from faker import Faker
from backend.models import Argument, ArgumentFieldValue, ArgumentLink, ArgumentTheme, ArgumentScheme, CriticalQuestion, User
from backend.utils import evaluate_and_propagate

faker = Faker("en_GB")

def seed_arguments(test=False):
    print("Seeding Arguments", end="\r")
    themes = list(ArgumentTheme.objects.all())
    if not themes:
        themes = [ArgumentTheme.get_or_create_other_theme()]
    cq_map = build_cq_map()
    for theme in themes:
        seed_theme_trees(theme, cq_map)
    evaluate_arguments()
    print("Argument seeding complete.")

def seed_theme_trees(theme, cq_map):
    users = get_users()
    schemes = get_schemes()
    if not schemes:
        return
    num_roots = random.randint(3, 5)
    for _ in range(num_roots):
        root = create_argument(theme, users, schemes)
        children = create_children(
            parent=root,
            theme=theme,
            users=users,
            schemes=schemes,
            cq_map=cq_map,
            min_children=2,
        )
        for child in children:
            create_children(
                parent=child,
                theme=theme,
                users=users,
                schemes=schemes,
                cq_map=cq_map,
                min_children=2,
            )

def create_argument(theme, users, schemes, root=True):
    scheme = random.choice(schemes)
    argument = Argument.objects.create(
        author=resolve_user(random.choice(users) if users else None),
        theme=theme,
        scheme=scheme,
        root=root,
    )
    populate_fields(argument, scheme)
    return argument


def populate_fields(argument, scheme):
    field_values = [
        ArgumentFieldValue(
            argument=argument,
            scheme_field=field,
            value=" ".join(faker.words(nb=random.randint(1, 4))),
        )
        for field in scheme.fields.all()
    ]
    ArgumentFieldValue.objects.bulk_create(field_values)

def create_children(parent, theme, users, schemes, cq_map, min_children=2):
    children = []
    cqs = cq_map.get(parent.scheme_id)
    if not cqs:
        return children
    num_children = random.randint(min_children, min_children + 1)
    for _ in range(num_children):
        child = create_argument(theme, users, schemes, False)
        cq = random.choice(cqs)
        ArgumentLink.objects.create(
            parent_argument=parent,
            child_argument=child,
            critical_question=cq,
            attacking=random.choice([True, False]),
        )
        children.append(child)
    return children

def build_cq_map():
    cq_map = {}
    for cq in CriticalQuestion.objects.select_related("scheme"):
        cq_map.setdefault(cq.scheme_id, []).append(cq)
    return cq_map

def get_users():
    return list(User.objects.all())

def get_schemes():
    return list(
        ArgumentScheme.objects.prefetch_related("fields")
    )

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def evaluate_arguments():
    for argument in Argument.objects.all():
        evaluate_and_propagate(argument)