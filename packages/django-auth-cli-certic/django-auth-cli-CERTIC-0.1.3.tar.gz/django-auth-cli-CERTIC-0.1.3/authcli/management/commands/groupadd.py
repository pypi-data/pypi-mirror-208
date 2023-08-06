from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument("identifier", help="identifiant de l'utilisateur")

    def handle(self, *args, **options):
        group_name = options["identifier"]
        group = Group.objects.filter(name=group_name).first()
        if group:
            raise CommandError("Le group existe déjà")

        group = Group.objects.create(name=group_name)
