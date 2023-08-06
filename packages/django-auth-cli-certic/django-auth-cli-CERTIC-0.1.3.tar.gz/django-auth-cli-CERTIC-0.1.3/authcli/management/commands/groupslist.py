from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth.models import Group
from django.core import serializers


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "-j", "--json", action="store_true", help="afficher les données en JSON"
        )
        parser.add_argument(
            "-s", "--separator", default="|", help="séparateur de champs"
        )

    def handle(self, *args, **options):
        print_as_json = options["json"]
        sep = options["separator"]
        q = Group.objects.all()
        if print_as_json:
            print(serializers.serialize("json", q, indent=2))
        else:
            print(f"id{sep}group")
            for group in q:
                print(f"{group.pk}{sep}{group.name}")
