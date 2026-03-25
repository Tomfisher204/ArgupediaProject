from django.db import models
from backend.models import Argument, CriticalQuestion

class ArgumentLink(models.Model):
    """Defines a link between two arguments in the graph."""
    parent_argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name="child_links")
    child_argument  = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name="parent_links")
    critical_question = models.ForeignKey(CriticalQuestion, on_delete=models.CASCADE)
    attacking = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)