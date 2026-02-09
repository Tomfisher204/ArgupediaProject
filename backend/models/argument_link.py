from django.db import models
from backend.models import ArgumentScheme, CriticalQuestion

class ArgumentLink(models.Model):
    """Defines an argument link in the graph."""
    parent_argument = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE, related_name="parent_links")
    child_argument = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE, related_name="child_links")
    critical_question = models.ForeignKey(CriticalQuestion, on_delete=models.CASCADE)
    attacking = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)