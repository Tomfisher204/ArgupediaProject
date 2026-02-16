from django.core.management.base import BaseCommandUser
from backend.models import User, ArgumentTheme, ArgumentScheme, SchemeField, Argument, ArgumentFieldValue, CriticalQuestion, ArgumentLink 

class Command(BaseCommand):
    help = 'Remove seeded data from the database'
    
    def handle(self, *args, **options):
        User.objects.all().delete()
        ArgumentTheme.objects.all().delete()
        ArgumentScheme.objects.all().delete()
        SchemeField.objects.all().delete()
        Argument.objects.all().delete()
        ArgumentFieldValue.objects.all().delete()
        CriticalQuestion.objects.all().delete()
        ArgumentLink.objects.all().delete()