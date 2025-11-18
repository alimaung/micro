"""
Django management command to drop the FilmingSessionLog table.

This command permanently removes the microapp_filmingsessionlog table from the database.
Logs are no longer stored in the database - they are only streamed via WebSocket.

WARNING: This operation is irreversible. All log data will be permanently deleted.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Drop the FilmingSessionLog table from the database (irreversible operation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt and drop the table immediately',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually dropping the table',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']
        
        table_name = 'microapp_filmingsessionlog'
        
        # Check if table exists
        with connection.cursor() as cursor:
            # Get database backend name
            db_backend = settings.DATABASES['default']['ENGINE']
            
            if 'sqlite' in db_backend.lower():
                # SQLite: Check if table exists (use %s for Django's parameterization)
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=%s
                """, [table_name])
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    # Get row count before deletion
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                else:
                    row_count = 0
            else:
                # PostgreSQL/MySQL: Check if table exists
                if 'postgresql' in db_backend.lower():
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, [table_name])
                    table_exists = cursor.fetchone()[0]
                elif 'mysql' in db_backend.lower():
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name = %s
                    """, [table_name])
                    table_exists = cursor.fetchone()[0] > 0
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Unknown database backend: {db_backend}')
                    )
                    table_exists = False
                
                if table_exists:
                    # Get row count before deletion
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                else:
                    row_count = 0
        
        if not table_exists:
            self.stdout.write(
                self.style.SUCCESS(f'Table "{table_name}" does not exist. Nothing to drop.')
            )
            return
        
        # Display information
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('DROP TABLE OPERATION'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(f'Table name: {table_name}')
        self.stdout.write(f'Current row count: {row_count:,}')
        self.stdout.write(f'Database backend: {db_backend}')
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
            self.stdout.write(f'Would execute: DROP TABLE IF EXISTS {table_name};')
            return
        
        # Confirmation prompt
        if not force:
            self.stdout.write(
                self.style.ERROR(
                    'WARNING: This will permanently delete the table and all its data!'
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    'This operation cannot be undone!'
                )
            )
            self.stdout.write('')
            
            confirm = input(
                f'Type "DROP {table_name}" to confirm: '
            )
            
            if confirm != f'DROP {table_name}':
                self.stdout.write(
                    self.style.ERROR('Confirmation failed. Operation cancelled.')
                )
                return
        
        # Drop the table
        try:
            with connection.cursor() as cursor:
                if 'sqlite' in db_backend.lower():
                    # SQLite: Drop table (SQLite doesn't support CASCADE)
                    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
                else:
                    # PostgreSQL/MySQL: Drop table with CASCADE to handle dependencies
                    cursor.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
                
                # Verify table was dropped
                if 'sqlite' in db_backend.lower():
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=%s
                    """, [table_name])
                    still_exists = cursor.fetchone() is not None
                elif 'postgresql' in db_backend.lower():
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, [table_name])
                    still_exists = cursor.fetchone()[0]
                elif 'mysql' in db_backend.lower():
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE() 
                        AND table_name = %s
                    """, [table_name])
                    still_exists = cursor.fetchone()[0] > 0
                else:
                    still_exists = False
                
                if still_exists:
                    raise CommandError(f'Failed to drop table {table_name}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully dropped table "{table_name}" '
                    f'({row_count:,} rows deleted)'
                )
            )
            
            # Suggest next steps
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Create a migration to reflect this change:')
            self.stdout.write('     python manage.py makemigrations --empty microapp')
            self.stdout.write('  2. Edit the migration to add the DeleteModel operation')
            self.stdout.write('  3. Run: python manage.py migrate')
            
        except Exception as e:
            raise CommandError(f'Error dropping table: {e}')

