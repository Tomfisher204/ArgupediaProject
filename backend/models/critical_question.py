from django.db import models
from backend.models import ArgumentScheme

class CriticalQuestion(models.Model):
    """Defines a critical question used to attack or support an argument."""
    scheme = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE)
    question = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)