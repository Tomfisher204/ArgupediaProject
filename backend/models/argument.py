from django.db import models
from backend.models import User, ArgumentTheme, SchemeField, ArgumentScheme

class Argument(models.Model):
    """Defines an argument."""
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=User.deleted_user)
    theme = models.ForeignKey(ArgumentTheme, on_delete=models.SET_DEFAULT, default=ArgumentTheme.get_or_create_other_theme)
    scheme = models.ForeignKey(ArgumentScheme, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    reported_by = models.ManyToManyField(User, related_name='reported_arguments', blank=True)
    is_winning = models.BooleanField(null=True, blank=True, default=None)
    root = models.BooleanField(default=False)

class ArgumentFieldValue(models.Model):
    """Defines the value for one field in an argument."""
    argument = models.ForeignKey(Argument, related_name="field_values", on_delete=models.CASCADE)
    scheme_field = models.ForeignKey(SchemeField, on_delete=models.CASCADE)
    value = models.TextField()