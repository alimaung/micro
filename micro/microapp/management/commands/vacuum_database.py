"""
Django management command to vacuum (compact) the SQLite database.

This command reclaims space after dropping tables or deleting large amounts of data.
SQLite doesn't automatically shrink the database file - VACUUM is required.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Vacuum the database to reclaim space after dropping tables or deleting data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually vacuuming',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get database info
        db_config = settings.DATABASES['default']
        db_backend = db_config['ENGINE']
        db_name = db_config.get('NAME', '')
        
        # Check if it's SQLite
        if 'sqlite' not in db_backend.lower():
            self.stdout.write(
                self.style.WARNING(
                    f'VACUUM is primarily for SQLite databases. '
                    f'Current backend: {db_backend}'
                )
            )
            response = input('Continue anyway? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
        
        # Get initial size
        if os.path.exists(db_name):
            initial_size = os.path.getsize(db_name)
            initial_size_mb = initial_size / (1024 * 1024)
        else:
            self.stdout.write(
                self.style.ERROR(f'Database file not found: {db_name}')
            )
            return
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('DATABASE VACUUM OPERATION'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(f'Database: {db_name}')
        self.stdout.write(f'Backend: {db_backend}')
        self.stdout.write(f'Initial size: {initial_size_mb:.2f} MB ({initial_size:,} bytes)')
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
            self.stdout.write('Would execute: VACUUM;')
            self.stdout.write('')
            self.stdout.write(
                'Note: VACUUM requires exclusive database access. '
                'Make sure no other processes are using the database.'
            )
            return
        
        # Warn about exclusive access
        self.stdout.write(
            self.style.WARNING(
                'WARNING: VACUUM requires exclusive database access.'
            )
        )
        self.stdout.write(
            'Make sure no other processes are using the database.'
        )
        self.stdout.write('')
        
        confirm = input('Continue with VACUUM? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return
        
        # Perform VACUUM
        try:
            self.stdout.write('Running VACUUM...')
            self.stdout.write('This may take a while for large databases...')
            
            with connection.cursor() as cursor:
                cursor.execute("VACUUM")
            
            # Get final size
            final_size = os.path.getsize(db_name)
            final_size_mb = final_size / (1024 * 1024)
            space_reclaimed = initial_size - final_size
            space_reclaimed_mb = space_reclaimed / (1024 * 1024)
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(self.style.SUCCESS('VACUUM COMPLETED'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(f'Initial size: {initial_size_mb:.2f} MB ({initial_size:,} bytes)')
            self.stdout.write(f'Final size: {final_size_mb:.2f} MB ({final_size:,} bytes)')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Space reclaimed: {space_reclaimed_mb:.2f} MB ({space_reclaimed:,} bytes)'
                )
            )
            if initial_size > 0:
                reduction_percent = (space_reclaimed / initial_size * 100)
                self.stdout.write(
                    self.style.SUCCESS(f'Reduction: {reduction_percent:.2f}%')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error vacuuming database: {e}')
            )
            self.stdout.write('')
            self.stdout.write(
                'Common causes:'
            )
            self.stdout.write('  - Another process is using the database')
            self.stdout.write('  - Insufficient disk space')
            self.stdout.write('  - Database file permissions issue')
            raise

