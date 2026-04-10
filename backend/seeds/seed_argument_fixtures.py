from backend.models import Argument, ArgumentFieldValue, ArgumentLink, ArgumentTheme, ArgumentScheme, CriticalQuestion, User
from backend.utils import evaluate_and_propagate

def get_users():
    return list(User.objects.all())

def resolve_user(user):
    if isinstance(user, User):
        return user
    return User.deleted_user()

def seed_argument_fixtures(test=False):
    print("Seeding Argument Fixtures", end="\r")
    generate_argument_fixtures()
    print("Argument Fixture seeding complete.")

def generate_argument_fixtures():
    users = get_users()
    deleted = User.deleted_user()
    author = users[0] if users else deleted
    theme, _ = ArgumentTheme.objects.get_or_create(title="Lockdown")
    schemes = list(ArgumentScheme.objects.prefetch_related("fields").all())
    cqs = list(CriticalQuestion.objects.all())
    argument_fixtures = [
        {
            "scheme": 0,
            "root": True,
            "author": author,
            "fields": {
                "Scenario (S)": "A pandemic",
                "Action (A)": "Lockdown",
                "Goal (G)": "Limits the spread of the virus",
                "Value (V)": "Public health",
            },
        },
        {
            "scheme": 1,
            "root": False,
            "author": author,
            "fields": {
                "Expert (E)": "Northbridge Infectious Risk Group",
                "Domain (D)": "Epidemiology",
                "Claim (C)": "Lockdowns significantly reduce transmission rates and peak infections",
            },
        },
        {
            "scheme": 1,
            "root": False,
            "author": author,
            "fields": {
                "Expert (E)": "Dr Lena Carter, Eastborough Institute for Economic Studies",
                "Domain (D)": "Macroeconomics",
                "Claim (C)": "Extended lockdowns can reduce output and increase unemployment over time",
            },
        },
        {
            "scheme": 2,
            "root": False,
            "author": author,
            "fields": {
                "Item A": "East Asian SARS-era movement controls",
                "Item B": "UK lockdown policy in a pandemic scenario",
                "Feature X": "Short-term economic slowdown and longer-term social disruption",
            },
        },
        {
            "scheme": 1,
            "root": False,
            "author": author,
            "fields": {
                "Expert (E)": "Dr Mira Solberg, Caldonia Public Health Lab",
                "Domain (D)": "Disease modelling",
                "Claim (C)": "Lockdowns can reduce peak infections by roughly 50–70% in simulation models",
            },
        },
        {
            "scheme": 1,
            "root": False,
            "author": author,
            "fields": {
                "Expert (E)": "Harbour Fiscal Observatory",
                "Domain (D)": "Public finance",
                "Claim (C)": "Targeted government support can offset much of the economic damage caused by lockdowns",
            },
        },
        {
            "scheme": 1,
            "root": False,
            "author": author,
            "fields": {
                "Expert (E)": "Dr Rowan Hale, independent policy researcher",
                "Domain (D)": "Research governance",
                "Claim (C)": "Institutional funding sources may bias pandemic policy research conclusions",
            },
        },
        {
            "scheme": 2,
            "root": False,
            "author": author,
            "fields": {
                "Item A": "Island-state containment strategy in a fictional pandemic response",
                "Item B": "UK national lockdown strategy in a pandemic scenario",
                "Feature X": "Fast reduction in cases followed by controlled reopening and low mortality",
            },
        },
    ]
    link_fixtures = [
        {"parent": 0, "child": 1, "cq": 0, "attacking": False},
        {"parent": 0, "child": 2, "cq": 1, "attacking": True},
        {"parent": 0, "child": 3, "cq": 1, "attacking": True},
        {"parent": 1, "child": 4, "cq": 4, "attacking": False},
        {"parent": 2, "child": 5, "cq": 6, "attacking": False},
        {"parent": 1, "child": 6, "cq": 5, "attacking": True},
        {"parent": 0, "child": 7, "cq": 3, "attacking": False},
    ]
    created = []
    for data in argument_fixtures:
        created.append(create_argument(data, theme, schemes))
    for data in link_fixtures:
        ArgumentLink.objects.create(
            parent_argument=created[data["parent"]],
            child_argument=created[data["child"]],
            critical_question=cqs[data["cq"]],
            attacking=data["attacking"],
        )
    for argument in created:
        evaluate_and_propagate(argument)

def create_argument(data, theme, schemes):
    scheme = schemes[data["scheme"]]
    argument = Argument.objects.create(
        author=resolve_user(data["author"]),
        theme=theme,
        scheme=scheme,
        root=data.get("root", False),
    )
    populate_fields(argument, scheme, data.get("fields", {}))
    return argument

def populate_fields(argument, scheme, fields):
    field_objects = {f.name: f for f in scheme.fields.all()}
    ArgumentFieldValue.objects.bulk_create([
        ArgumentFieldValue(
            argument=argument,
            scheme_field=field_objects[name],
            value=value,
        )
        for name, value in fields.items()
    ])