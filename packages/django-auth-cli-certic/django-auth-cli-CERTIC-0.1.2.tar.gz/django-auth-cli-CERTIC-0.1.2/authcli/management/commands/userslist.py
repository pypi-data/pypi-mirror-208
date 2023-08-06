from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.contrib.auth.models import User
from django.core import serializers


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "-a",
            "--active",
            action="store_true",
            help="afficher uniquement les utilisateurs actifs",
        )
        parser.add_argument(
            "-j", "--json", action="store_true", help="afficher les données en JSON"
        )
        parser.add_argument(
            "-s", "--separator", default="|", help="séparateur de champs"
        )

    def handle(self, *args, **options):
        only_active = options["active"]
        print_as_json = options["json"]
        sep = options["separator"]
        q = User.objects.all()
        if only_active:
            q = User.objects.filter(is_active=True)
        if print_as_json:
            print(serializers.serialize("json", q, indent=2))
        else:
            print(f"id{sep}user{sep}actif{sep}dernière connexion")
            for user in q:
                print(
                    f"{user.pk}{sep}{user.username}{sep}{'actif' if user.is_active else 'inactif'}{sep}{user.last_login}"
                )
