from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from microapp.models import FilmingSession


class Command(BaseCommand):
    help = 'Get all log messages from a specific filming session (logs are no longer stored in database - only available via WebSocket)'

    def add_arguments(self, parser):
        parser.add_argument(
            'session_id',
            type=str,
            help='The session ID to get logs for (e.g., a81ecb50-b3df-491d-98d7-92a47f20adb7)'
        )
        parser.add_argument(
            '--level',
            type=str,
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            help='Filter logs by level (optional) - not applicable, logs are not stored'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['detailed', 'simple', 'json'],
            default='detailed',
            help='Output format (default: detailed)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of log entries returned - not applicable, logs are not stored'
        )

    def handle(self, *args, **options):
        session_id = options['session_id']
        output_format = options['format']
        
        try:
            # Get the filming session
            session = FilmingSession.objects.get(session_id=session_id)
        except FilmingSession.DoesNotExist:
            raise CommandError(f'Filming session with ID "{session_id}" does not exist')
        
        # Logs are no longer stored in database - only available via WebSocket streaming
        message = (
            f"Logs for session {session_id} are not stored in the database.\n"
            f"Logs are only available via WebSocket streaming during active sessions.\n"
            f"No historical logs are maintained."
        )
        
        if output_format == 'json':
            import json
            self.stdout.write(json.dumps({
                'session_id': session_id,
                'message': message,
                'logs': []
            }))
        else:
            self.stdout.write(self.style.WARNING(message)) 