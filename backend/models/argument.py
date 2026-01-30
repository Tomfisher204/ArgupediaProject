from django.db import models
from ..models.societies import User, Theme, SchemeField, ArgumentScheme

class Argument(models.Model):
    """Defines an argument."""
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=User.deleted_user)
    theme = models.ForeignKey(Theme, on_delete=models.SET_DEFAULT, default=Theme.get_or_create_other_theme)
    scheme = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

class ArgumentFieldValue(models.Model):
    """Defines the value for one field in an argument."""
    argument = models.ForeignKey(Argument, related_name="field_values", on_delete=models.CASCADE)
    scheme_field = models.ForeignKey(SchemeField, on_delete=models.CASCADE)
    value = models.TextField()