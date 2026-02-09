from django.db import models
from backend.models import User

class ArgumentScheme(models.Model):
    """Defines an argument scheme."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=User.deleted_user)
    date_created = models.DateTimeField(auto_now_add=True)

class SchemeField(models.Model):
    """Defines one field in a scheme"""
    scheme = models.ForeignKey(ArgumentScheme, related_name="fields",on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

