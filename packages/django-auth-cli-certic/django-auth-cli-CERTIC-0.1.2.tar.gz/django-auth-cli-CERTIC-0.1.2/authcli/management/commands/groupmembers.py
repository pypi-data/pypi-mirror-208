from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "-s", "--separator", default="|", help="séparateur de champs"
        )

    def handle(self, *args, **options):
        sep = options["separator"]
        q = Group.objects.order_by("name")
        print(f"groupe{sep}membres")
        for group in q:
            members = []
            for u in group.user_set.order_by("username"):
                members.append(u.username)
            print(f"{group.name}{sep}{', '.join(members)}")
