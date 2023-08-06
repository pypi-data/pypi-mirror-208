from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument("user", help="identifiant de l'utilisateur (nom ou id)")
        parser.add_argument("group", help="identifiant du groupe (nom ou id)")

    def handle(self, *args, **options):
        user_id = options["user"]
        group_id = options["group"]

        try:
            as_int = int(user_id)
        except ValueError:
            as_int = None
        if as_int:
            q = User.objects.filter(pk=as_int)
        else:
            q = User.objects.filter(username=user_id)
        if q.count() == 0:
            raise CommandError("Utilisateur introuvable")
        user: User = q.first()

        try:
            as_int = int(group_id)
        except ValueError:
            as_int = None
        if as_int:
            q = Group.objects.filter(pk=as_int)
        else:
            q = Group.objects.filter(name=group_id)
        if q.count() == 0:
            raise CommandError("Groupe introuvable")
        group: Group = q.first()
        group.user_set.remove(user)
