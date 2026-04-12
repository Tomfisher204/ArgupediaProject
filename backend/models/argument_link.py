import threading
from django.db import models
from backend.models import Argument, CriticalQuestion

class ArgumentLink(models.Model):
    """Defines a link between two arguments in the graph."""
    parent_argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name="child_links")
    child_argument  = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name="parent_links")
    critical_question = models.ForeignKey(CriticalQuestion, on_delete=models.CASCADE)
    attacking = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    _thread_local = threading.local()

    def save(self, *args, **kwargs):
        creating = self._state.adding
        reciprocal_mode = getattr(self._thread_local, "creating_two_way", False)
        super().save(*args, **kwargs)
        if creating and not reciprocal_mode and self.critical_question.two_way:
            reciprocal = ArgumentLink.objects.filter(
                parent_argument=self.child_argument,
                child_argument=self.parent_argument,
                critical_question=self.critical_question,
                attacking=self.attacking,
            ).exists()
            if not reciprocal:
                try:
                    self._thread_local.creating_two_way = True
                    ArgumentLink(
                        parent_argument=self.child_argument,
                        child_argument=self.parent_argument,
                        critical_question=self.critical_question,
                        attacking=self.attacking,
                    ).save()
                finally:
                    self._thread_local.creating_two_way = False