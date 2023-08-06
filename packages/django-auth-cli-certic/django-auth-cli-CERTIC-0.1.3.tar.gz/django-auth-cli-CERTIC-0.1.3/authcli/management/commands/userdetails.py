from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.contrib.auth.models import User
from django.core import serializers


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "identifier", help="identifiant de l'utilisateur (nom ou id)"
        )

    def handle(self, *args, **options):
        identifier = options["identifier"]
        try:
            as_int = int(identifier)
        except ValueError:
            as_int = None
        if as_int:
            q = User.objects.filter(pk=as_int)
        else:
            q = User.objects.filter(username__icontains=identifier)
        if q.count() == 0:
            raise CommandError("Utilisateur introuvable")
        print(serializers.serialize("json", q, indent=2))
