from django.core.management.base import BaseCommand
from django.utils import timezone
from microapp.models import Roll


class Command(BaseCommand):
    help = 'Update all rolls to have filming_status=completed so they appear in development dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all rolls that don't have filming_status='completed'
        rolls_to_update = Roll.objects.exclude(filming_status='completed')
        
        if not rolls_to_update.exists():
            self.stdout.write(
                self.style.SUCCESS('All rolls already have filming_status=completed')
            )
            return
        
        self.stdout.write(f'Found {rolls_to_update.count()} rolls to update:')
        
        for roll in rolls_to_update:
            self.stdout.write(
                f'  - Roll {roll.film_number} ({roll.film_type}): '
                f'{roll.filming_status} -> completed, progress: {roll.filming_progress_percent}% -> 100%'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No changes made. Use without --dry-run to apply changes.')
            )
            return
        
        # Update all rolls
        updated_count = rolls_to_update.update(
            filming_status='completed',
            filming_progress_percent=100.0,
            filming_completed_at=timezone.now()
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} rolls to filming_status=completed with 100% progress'
            )
        ) 