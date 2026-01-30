from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.core.validators import EmailValidator

class User(AbstractUser):
    "Defines a user in the system."
    password_validator = RegexValidator(r'^(?=.*[A-Z])(?=.*\d)', 'Password must contain at least one uppercase letter and one number.')
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=False, validators=[EmailValidator()])
    password = models.CharField(max_length=50, validators=[MinLengthValidator(8), password_validator])
    is_admin = models.BooleanField(default=False)

    @classmethod
    def deleted_user():
        """Returns a deleted user instance"""
        user, _ = User.objects.get_or_create(username = "deleted_user", defaults = {
            'first_name': 'Deleted', 
            'last_name': 'User', 
            'email': 'deleted@example.com'
        })
        return user.id