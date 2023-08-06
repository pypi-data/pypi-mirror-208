import os
from pathlib import Path

from django.core.management import BaseCommand

from core import settings
from core.helpers.template import generate_template


class Command(BaseCommand):
    help = "Allow refresh template files"

    def add_arguments(self, parser):
        parser.add_argument('--yaml', type=None, help='Indicates the yaml file to refresh template.')

    def handle(self, *args, **options):
        yaml = options['yaml']
        yaml_files = Path(settings.BASE_DIR).glob("**/*.yaml")
        for yaml_file in yaml_files:
            path = str(yaml_file)
            print("refresh template file: %s" % path)
            generate_template(path)
