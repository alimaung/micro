from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from microapp.models import FilmingSession, FilmingSessionLog


class Command(BaseCommand):
    help = 'Get all log messages from a specific filming session'

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
            help='Filter logs by level (optional)'
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
            help='Limit the number of log entries returned'
        )

    def handle(self, *args, **options):
        session_id = options['session_id']
        level_filter = options.get('level')
        output_format = options['format']
        limit = options.get('limit')
        
        try:
            # Get the filming session
            session = FilmingSession.objects.get(session_id=session_id)
        except FilmingSession.DoesNotExist:
            raise CommandError(f'Filming session with ID "{session_id}" does not exist')
        
        # Get logs for the session in reverse order (oldest first)
        logs_query = FilmingSessionLog.objects.filter(session=session).order_by('created_at')
        
        # Apply level filter if specified
        if level_filter:
            logs_query = logs_query.filter(level=level_filter)
        
        # Apply limit if specified
        if limit:
            logs_query = logs_query[:limit]
        
        logs = list(logs_query)
        
        if not logs:
            return
        
        # Display logs based on format
        if output_format == 'simple':
            self._display_simple_format(logs, level_filter)
        elif output_format == 'json':
            self._display_json_format(logs)
        else:  # detailed format
            self._display_detailed_format(logs, level_filter)

    def _display_detailed_format(self, logs, level_filter):
        """Display logs in detailed format"""
        for log in logs:
            self.stdout.write(log.message)

    def _display_simple_format(self, logs, level_filter):
        """Display logs in simple format"""
        for log in logs:
            self.stdout.write(log.message)

    def _display_json_format(self, logs):
        """Display logs in JSON format"""
        for log in logs:
            self.stdout.write(log.message) 