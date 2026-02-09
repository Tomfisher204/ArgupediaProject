from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator

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
    password_validator = RegexValidator(
        r'^(?=.*[A-Z])(?=.*\d)', 
        'Password must contain at least one uppercase letter and one number.'
    )

    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=False, validators=[EmailValidator()])
    password = models.CharField(max_length=50, validators=[MinLengthValidator(8), password_validator])
    is_admin = models.BooleanField(default=False)

    @classmethod
    def deleted_user(cls):
        """Returns a deleted user instance"""
        user, _ = cls.objects.get_or_create(
            username="deleted_user",
            defaults={
                'first_name': 'Deleted',
                'last_name': 'User',
                'email': 'deleted@example.com'
            }
        )
        return user.id