from django.core.management.base import BaseCommand
from backend.seeds import seed_all

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        seed_all()