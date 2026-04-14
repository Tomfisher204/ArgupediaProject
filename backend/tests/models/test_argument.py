from django.test import TestCase
from django.utils import timezone
from backend.models import User, ArgumentScheme, ArgumentTheme, SchemeField, Argument, ArgumentFieldValue

def make_user(username="test_user", email="test@example.com", **kwargs):
    return User.objects.create(
        username=username,
        first_name="Test",
        last_name="User",
        email=email,
        password="Password123",
        **kwargs,
    )

def make_scheme(name="Test Scheme", created_by=None):
    return ArgumentScheme.objects.create(
        name=name,
        created_by=created_by or make_user(username=f"scheme_creator_{name}", email=f"sc_{name}@example.com"),
    )

def make_theme(title="Science", creator=None):
    return ArgumentTheme.objects.create(
        title=title,
        creator=creator or make_user(username=f"theme_creator_{title}", email=f"tc_{title}@example.com"),
    )

class ArgumentModelTests(TestCase):
    """Tests for the Argument model validation and functionality."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)

    def test_create_argument(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.assertEqual(arg.author, self.user)
        self.assertEqual(arg.scheme, self.scheme)
        self.assertEqual(arg.theme, self.theme)

    def test_is_winning_defaults_to_none(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.assertIsNone(arg.is_winning)

    def test_root_defaults_to_false(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.assertFalse(arg.root)

    def test_date_created_auto_set(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.assertIsNotNone(arg.date_created)
        self.assertLessEqual(arg.date_created, timezone.now())

    def test_author_defaults_to_deleted_user_on_deletion(self):
        author = make_user(username="author_to_delete", email="author_del@example.com")
        arg = Argument.objects.create(author=author, scheme=self.scheme, theme=self.theme)
        author.delete()
        arg.refresh_from_db()
        self.assertEqual(arg.author_id, User.deleted_user())

    def test_theme_defaults_to_other_on_deletion(self):
        theme = make_theme(title="Temp Theme")
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=theme)
        theme.delete()
        arg.refresh_from_db()
        other_theme = ArgumentTheme.objects.get(title="Other")
        self.assertEqual(arg.theme, other_theme)

    def test_reported_by_many_to_many(self):
        reporter1 = make_user(username="reporter1", email="rep1@example.com")
        reporter2 = make_user(username="reporter2", email="rep2@example.com")
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        arg.reported_by.add(reporter1, reporter2)
        self.assertIn(reporter1, arg.reported_by.all())
        self.assertIn(reporter2, arg.reported_by.all())

    def test_reported_by_is_optional(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.assertEqual(arg.reported_by.count(), 0)

    def test_cascade_delete_with_scheme(self):
        arg = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        arg_id = arg.id
        self.scheme.delete()
        self.assertFalse(Argument.objects.filter(id=arg_id).exists())


class ArgumentFieldValueModelTests(TestCase):
    """Tests for the ArgumentFieldValue model validation and functionality."""

    def setUp(self):
        self.user = make_user()
        self.scheme = make_scheme(created_by=self.user)
        self.theme = make_theme(creator=self.user)
        self.argument = Argument.objects.create(author=self.user, scheme=self.scheme, theme=self.theme)
        self.field = SchemeField.objects.create(scheme=self.scheme, name="Premise", order=1)

    def test_create_field_value(self):
        afv = ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value="All men are mortal.")
        self.assertEqual(afv.value, "All men are mortal.")
        self.assertEqual(afv.argument, self.argument)
        self.assertEqual(afv.scheme_field, self.field)

    def test_value_can_be_long_text(self):
        long_value = "x" * 5000
        afv = ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value=long_value)
        self.assertEqual(len(afv.value), 5000)

    def test_cascade_delete_with_argument(self):
        afv = ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value="To be deleted")
        afv_id = afv.id
        self.argument.delete()
        self.assertFalse(ArgumentFieldValue.objects.filter(id=afv_id).exists())

    def test_multiple_field_values_per_argument(self):
        field2 = SchemeField.objects.create(scheme=self.scheme, name="Conclusion", order=2)
        ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value="Premise value")
        ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=field2, value="Conclusion value")
        self.assertEqual(ArgumentFieldValue.objects.filter(argument=self.argument).count(), 2)

    def test_related_name_field_values(self):
        ArgumentFieldValue.objects.create(argument=self.argument, scheme_field=self.field, value="Test")
        self.assertEqual(self.argument.field_values.count(), 1)