from django.core.management.base import BaseCommand
from backend.models import User, ArgumentTheme, ArgumentScheme, SchemeField, Argument, ArgumentFieldValue, CriticalQuestion, ArgumentLink

class Command(BaseCommand):
    help = 'Remove seeded data from the database'
    
    def handle(self, *args, **options):
        ArgumentLink.objects.all().delete()
        ArgumentFieldValue.objects.all().delete()
        CriticalQuestion.objects.all().delete()
        Argument.objects.all().delete()
        SchemeField.objects.all().delete()
        ArgumentScheme.objects.all().delete()
        ArgumentTheme.objects.all().delete()
        User.objects.all().delete()