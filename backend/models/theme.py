from django.db import models
from ..models.societies import User

class ArgumentTopic(models.Model):
    """Defines a theme for arguments."""
    title = models.CharField(max_length=100, unique=True, default="Other")
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=User.deleted_user)

    @classmethod
    def get_or_create_other_topic(cls):
        """Returns the 'Other' argument topic instance."""
        topic, _ = ArgumentTopic.objects.get_or_create(title="Other")
        return topic