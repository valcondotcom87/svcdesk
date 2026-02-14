from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.sessions.models import Session

from apps.users.models import User


class Command(BaseCommand):
    help = "Force logout a user by invalidating JWT tokens and optionally clearing sessions."

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='User email address')
        parser.add_argument('--user-id', type=str, help='User UUID')
        parser.add_argument(
            '--clear-sessions',
            action='store_true',
            help='Delete active Django sessions for the user',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        user_id = options.get('user_id')
        clear_sessions = options.get('clear_sessions')

        if not email and not user_id:
            raise CommandError('Provide --email or --user-id')

        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise CommandError('User not found') from exc

        User.objects.filter(id=user.id).update(password_changed_at=timezone.now())

        cleared = 0
        if clear_sessions:
            for session in Session.objects.filter(expire_date__gte=timezone.now()):
                data = session.get_decoded()
                if str(data.get('_auth_user_id')) == str(user.id):
                    session.delete()
                    cleared += 1

        message = f"Forced logout for {user.email}."
        if clear_sessions:
            message = f"{message} Cleared {cleared} session(s)."
        self.stdout.write(self.style.SUCCESS(message))
