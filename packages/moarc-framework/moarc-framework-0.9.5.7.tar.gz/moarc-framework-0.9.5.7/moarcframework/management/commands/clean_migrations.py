import os
from pathlib import Path

from django.core.management import BaseCommand

from core import settings


class Command(BaseCommand):
    help = "Allow clean migrations"

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        migrations = Path(settings.BASE_DIR).glob("**/*migrations*/0*")
        for migration in migrations:
            path = str(migration)
            print("Cleaning migration: %s" % path)
            os.remove(path)
