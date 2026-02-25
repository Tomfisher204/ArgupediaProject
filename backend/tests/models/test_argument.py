from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import (
    User,
    ArgumentTheme,
    ArgumentScheme,
    SchemeField,
    Argument,
    ArgumentFieldValue,
    ArgumentVote
)


class ArgumentModelTests(TestCase):
    """Tests for the Argument model and related models."""

    def setUp(self):
        self.user = User.objects.create(
            username="author_user",
            first_name="Author",
            last_name="User",
            email="author@example.com",
            password="Password123"
        )
        self.other_user = User.objects.create(
            username="voter_user",
            first_name="Voter",
            last_name="User",
            email="voter@example.com",
            password="Password123"
        )
        self.theme = ArgumentTheme.objects.create(
            title="Politics",
            description="Political debates",
            creator=self.user
        )
        self.scheme = ArgumentScheme.objects.create(
            name="Causal Scheme",
            description="Cause and effect reasoning",
            created_by=self.user
        )
        self.scheme_field = SchemeField.objects.create(
            scheme=self.scheme,
            name="Premise"
        )
        self.valid_argument_data = {
            "author": self.user,
            "theme": self.theme,
            "scheme": self.scheme
        }

    def test_create_argument(self):
        """Test that an Argument can be created successfully."""
        argument = Argument.objects.create(**self.valid_argument_data)
        self.assertEqual(argument.author, self.user)
        self.assertEqual(argument.theme, self.theme)
        self.assertEqual(argument.scheme, self.scheme)
        self.assertIsNotNone(argument.date_created)

    def test_argument_default_author(self):
        """Test that author defaults to deleted_user if not provided."""
        argument = Argument.objects.create(
            theme=self.theme,
            scheme=self.scheme
        )
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(argument.author, deleted_user)

    def test_argument_default_theme(self):
        """Test that theme defaults to 'Other' if not provided."""
        argument = Argument.objects.create(
            author=self.user,
            scheme=self.scheme
        )
        other_theme = ArgumentTheme.objects.get(title="Other")
        self.assertEqual(argument.theme, other_theme)

    def test_argument_deleted_when_scheme_deleted(self):
        """Test that Argument is deleted when related scheme is deleted."""
        argument = Argument.objects.create(**self.valid_argument_data)
        self.scheme.delete()
        self.assertEqual(Argument.objects.count(), 0)

    def test_argument_author_set_default_on_delete(self):
        """Test that author is set to deleted_user when original author is deleted."""
        argument = Argument.objects.create(**self.valid_argument_data)
        self.user.delete()
        argument.refresh_from_db()
        deleted_user = User.objects.get(username="deleted_user")
        self.assertEqual(argument.author, deleted_user)

    def test_argument_theme_set_default_on_delete(self):
        """Test that theme is set to 'Other' when original theme is deleted."""
        argument = Argument.objects.create(**self.valid_argument_data)
        self.theme.delete()
        argument.refresh_from_db()
        other_theme = ArgumentTheme.objects.get(title="Other")
        self.assertEqual(argument.theme, other_theme)


class ArgumentFieldValueModelTests(TestCase):
    """Tests for the ArgumentFieldValue model."""

    def setUp(self):
        self.user = User.objects.create(
            username="field_user",
            first_name="Field",
            last_name="User",
            email="field@example.com",
            password="Password123"
        )
        self.scheme = ArgumentScheme.objects.create(
            name="Analogical Scheme",
            description="Arguments by analogy",
            created_by=self.user
        )
        self.scheme_field = SchemeField.objects.create(
            scheme=self.scheme,
            name="Conclusion"
        )
        self.argument = Argument.objects.create(
            author=self.user,
            scheme=self.scheme
        )

    def test_create_argument_field_value(self):
        """Test that an ArgumentFieldValue can be created successfully."""
        field_value = ArgumentFieldValue.objects.create(
            argument=self.argument,
            scheme_field=self.scheme_field,
            value="This is the conclusion."
        )
        self.assertEqual(field_value.argument, self.argument)
        self.assertEqual(field_value.scheme_field, self.scheme_field)
        self.assertEqual(field_value.value, "This is the conclusion.")

    def test_field_value_deleted_with_argument(self):
        """Test that ArgumentFieldValue is deleted when Argument is deleted."""
        ArgumentFieldValue.objects.create(
            argument=self.argument,
            scheme_field=self.scheme_field,
            value="Some value"
        )
        self.argument.delete()
        self.assertEqual(ArgumentFieldValue.objects.count(), 0)


class ArgumentVoteModelTests(TestCase):
    """Tests for the ArgumentVote model."""

    def setUp(self):
        self.user = User.objects.create(
            username="vote_author",
            first_name="Vote",
            last_name="Author",
            email="vote_author@example.com",
            password="Password123"
        )
        self.voter = User.objects.create(
            username="vote_user",
            first_name="Vote",
            last_name="User",
            email="vote_user@example.com",
            password="Password123"
        )
        self.scheme = ArgumentScheme.objects.create(
            name="Ethical Scheme",
            description="Ethical reasoning",
            created_by=self.user
        )
        self.argument = Argument.objects.create(
            author=self.user,
            scheme=self.scheme
        )

    def test_create_argument_vote(self):
        """Test that an ArgumentVote can be created successfully."""
        vote = ArgumentVote.objects.create(
            argument=self.argument,
            user=self.voter,
            is_upvote=True
        )
        self.assertEqual(vote.argument, self.argument)
        self.assertEqual(vote.user, self.voter)
        self.assertTrue(vote.is_upvote)

    def test_vote_deleted_with_argument(self):
        """Test that votes are deleted when Argument is deleted."""
        ArgumentVote.objects.create(
            argument=self.argument,
            user=self.voter,
            is_upvote=True
        )
        self.argument.delete()
        self.assertEqual(ArgumentVote.objects.count(), 0)

    def test_vote_deleted_with_user(self):
        """Test that votes are deleted when User is deleted."""
        ArgumentVote.objects.create(
            argument=self.argument,
            user=self.voter,
            is_upvote=True
        )
        self.voter.delete()
        self.assertEqual(ArgumentVote.objects.count(), 0)

    def test_related_name_votes(self):
        """Test that related_name 'votes' works correctly."""
        vote1 = ArgumentVote.objects.create(
            argument=self.argument,
            user=self.voter,
            is_upvote=True
        )
        vote2 = ArgumentVote.objects.create(
            argument=self.argument,
            user=self.user,
            is_upvote=False
        )
        self.assertEqual(self.argument.votes.count(), 2)
        self.assertIn(vote1, self.argument.votes.all())
        self.assertIn(vote2, self.argument.votes.all())