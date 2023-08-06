from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.contrib.auth.models import Group
from django.core import serializers


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument("identifier", help="identifiant du groupe (nom ou id)")

    def handle(self, *args, **options):
        identifier = options["identifier"]
        try:
            as_int = int(identifier)
        except ValueError:
            as_int = None
        if as_int:
            q = Group.objects.filter(pk=as_int)
        else:
            q = Group.objects.filter(name__icontains=identifier)
        if q.count() == 0:
            raise CommandError("Groupe introuvable")
        print(serializers.serialize("json", q, indent=2))
