from django.db import models
from ..models.societies import ArgumentScheme, CriticalQuestion

class ArgumentLink(models.Model):
    """Defines an argument link in the graph."""
    parent_argument = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE)
    child_argument = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE)
    critical_question = models.ForeignKey(CriticalQuestion, on_delete=models.CASCADE)
    attacking = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)