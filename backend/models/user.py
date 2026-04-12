import re
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """Defines a user in the system."""

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=False, validators=[EmailValidator()])
    password = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)

    @classmethod
    def deleted_user(cls):
        """Returns a deleted user instance"""
        user, _ = cls.objects.get_or_create(
            username="deleted_user",
            defaults={'first_name': 'Deleted', 'last_name': 'User', 'email': 'deleted@example.com'}
        )
        return user.id
    def clean(self):
        """Custom validation for the password field using Django's validators."""
        super().clean()
        if self.password:
            password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,}$'
            if not re.match(password_regex, self.password):
                raise ValidationError({'password': "Password must be at least 8 characters long, contain at least one uppercase letter and one number."})