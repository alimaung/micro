"""
Management command to restore temp rolls that were invalidated during re-filming.

This command fixes the issue where temp rolls were unnecessarily invalidated when
rolls were re-filmed, even though the physical temp roll still exists and is usable.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from microapp.models import TempRoll
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Restore temp rolls that were invalidated during re-filming back to their correct status (available or used)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each temp roll being processed',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Searching for invalidated temp rolls...')
        )
        
        # Find all temp rolls with invalidated_refilm status
        invalidated_temp_rolls = TempRoll.objects.filter(status='invalidated_refilm')
        
        if not invalidated_temp_rolls.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ No invalidated temp rolls found. All temp rolls are in good condition!')
            )
            return
        
        count = invalidated_temp_rolls.count()
        self.stdout.write(
            self.style.WARNING(f'📋 Found {count} temp roll(s) that were invalidated during re-filming')
        )
        
        # Categorize temp rolls by their correct status
        available_temp_rolls = invalidated_temp_rolls.filter(used_by_roll__isnull=True)
        used_temp_rolls = invalidated_temp_rolls.filter(used_by_roll__isnull=False)
        
        if verbose or dry_run:
            self.stdout.write('\nDetails:')
            for temp_roll in invalidated_temp_rolls:
                source_info = f" (from roll {temp_roll.source_roll.roll_number})" if temp_roll.source_roll else ""
                used_info = f", used by roll {temp_roll.used_by_roll.roll_number}" if temp_roll.used_by_roll else ", unused"
                correct_status = "used" if temp_roll.used_by_roll else "available"
                self.stdout.write(
                    f"  • Temp Roll #{temp_roll.temp_roll_id}: {temp_roll.film_type}, "
                    f"{temp_roll.usable_capacity} pages{source_info}{used_info} → {correct_status}"
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🧪 DRY RUN: No changes were made. Run without --dry-run to apply changes.')
            )
            return
        
        # Show summary of what will be restored
        if available_temp_rolls.exists() or used_temp_rolls.exists():
            self.stdout.write(f'\nWill restore:')
            if available_temp_rolls.exists():
                self.stdout.write(f'  • {available_temp_rolls.count()} temp roll(s) to "available" status')
            if used_temp_rolls.exists():
                self.stdout.write(f'  • {used_temp_rolls.count()} temp roll(s) to "used" status')
        
        # Confirm before making changes
        if not options.get('verbosity', 1) == 0:  # Only ask if not running silently
            confirm = input(f'\nRestore {count} temp roll(s) to their correct status? (y/N): ')
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write(self.style.ERROR('❌ Operation cancelled'))
                return
        
        # Restore temp rolls to their correct status
        try:
            with transaction.atomic():
                updated_available = 0
                updated_used = 0
                
                # Restore unused temp rolls to 'available'
                if available_temp_rolls.exists():
                    updated_available = available_temp_rolls.update(status='available')
                
                # Restore used temp rolls to 'used'  
                if used_temp_rolls.exists():
                    updated_used = used_temp_rolls.update(status='used')
                
                total_updated = updated_available + updated_used
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully restored {total_updated} temp roll(s):')
                )
                if updated_available > 0:
                    self.stdout.write(f'  • {updated_available} temp roll(s) set to "available"')
                if updated_used > 0:
                    self.stdout.write(f'  • {updated_used} temp roll(s) set to "used"')
                
                # Log the details if verbose
                if verbose:
                    self.stdout.write('\nRestored temp rolls:')
                    for temp_roll in TempRoll.objects.filter(
                        temp_roll_id__in=invalidated_temp_rolls.values_list('temp_roll_id', flat=True)
                    ):
                        source_info = f" (from roll {temp_roll.source_roll.roll_number})" if temp_roll.source_roll else ""
                        used_info = f", used by roll {temp_roll.used_by_roll.roll_number}" if temp_roll.used_by_roll else ""
                        self.stdout.write(
                            f"  ✓ Temp Roll #{temp_roll.temp_roll_id}: {temp_roll.film_type}, "
                            f"{temp_roll.usable_capacity} pages{source_info}{used_info} → {temp_roll.status}"
                        )
                
                # Provide summary statistics
                total_available = TempRoll.objects.filter(status='available').count()
                total_used = TempRoll.objects.filter(status='used').count()
                total_invalidated = TempRoll.objects.filter(status='invalidated_refilm').count()
                
                available_capacity = sum(
                    TempRoll.objects.filter(status='available').values_list('usable_capacity', flat=True) or [0]
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n📊 Current temp roll status:'
                        f'\n  • Available: {total_available} temp rolls ({available_capacity} usable pages)'
                        f'\n  • Used: {total_used} temp rolls'
                        f'\n  • Still invalidated: {total_invalidated} temp rolls'
                    )
                )
                
        except Exception as e:
            logger.error(f"Error restoring temp rolls: {e}")
            raise CommandError(f'Failed to restore temp rolls: {e}') 