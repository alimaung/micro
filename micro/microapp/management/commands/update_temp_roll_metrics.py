"""
Management command to update temp roll metrics for existing analyzed folders.

This command recalculates temp roll estimates for all analyzed folders that don't have
temp roll data or have outdated temp roll calculations.

Usage:
    python manage.py update_temp_roll_metrics
    python manage.py update_temp_roll_metrics --force  # Recalculate all, even if data exists
    python manage.py update_temp_roll_metrics --folder-id 123  # Update specific folder
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from microapp.models import AnalyzedFolder
from microapp.services.analyze_service import AnalyzeService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update temp roll metrics for existing analyzed folders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recalculate temp roll metrics for all folders, even if data already exists',
        )
        parser.add_argument(
            '--folder-id',
            type=int,
            help='Update temp roll metrics for a specific analyzed folder ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        force = options['force']
        folder_id = options.get('folder_id')
        dry_run = options['dry_run']

        analyze_service = AnalyzeService()

        # Get folders to update
        if folder_id:
            try:
                folders = [AnalyzedFolder.objects.get(id=folder_id)]
                self.stdout.write(f"Updating specific folder ID: {folder_id}")
            except AnalyzedFolder.DoesNotExist:
                raise CommandError(f"Analyzed folder with ID {folder_id} does not exist")
        else:
            if force:
                folders = AnalyzedFolder.objects.all()
                self.stdout.write("Updating ALL analyzed folders (force mode)")
            else:
                # Only update folders that don't have temp roll data
                folders = AnalyzedFolder.objects.filter(
                    estimated_temp_rolls_created=0,
                    estimated_temp_rolls_used=0,
                    temp_roll_strategy='unknown'
                )
                self.stdout.write("Updating analyzed folders without temp roll data")

        total_folders = folders.count()
        if total_folders == 0:
            self.stdout.write(
                self.style.WARNING("No analyzed folders found to update.")
            )
            return

        self.stdout.write(f"Found {total_folders} folders to process")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        updated_count = 0
        error_count = 0

        for i, folder in enumerate(folders, 1):
            if self.verbosity >= 1:
                self.stdout.write(f"Processing {i}/{total_folders}: {folder.folder_name}")

            try:
                old_data = {
                    'created': folder.estimated_temp_rolls_created,
                    'used': folder.estimated_temp_rolls_used,
                    'strategy': folder.temp_roll_strategy
                }

                # Calculate new temp roll metrics
                temp_roll_data = analyze_service._calculate_temp_roll_estimates(
                    folder.estimated_rolls_16mm,
                    folder.estimated_rolls_35mm,
                    folder.total_pages,
                    folder.has_oversized
                )

                new_data = {
                    'created': temp_roll_data['temp_rolls_created'],
                    'used': temp_roll_data['temp_rolls_used'],
                    'strategy': temp_roll_data['strategy']
                }

                # Check if data changed
                data_changed = (
                    old_data['created'] != new_data['created'] or
                    old_data['used'] != new_data['used'] or
                    old_data['strategy'] != new_data['strategy']
                )

                if self.verbosity >= 2:
                    self.stdout.write(f"  Old: {old_data}")
                    self.stdout.write(f"  New: {new_data}")
                    self.stdout.write(f"  Changed: {data_changed}")

                if data_changed or force:
                    if not dry_run:
                        with transaction.atomic():
                            folder.estimated_temp_rolls_created = new_data['created']
                            folder.estimated_temp_rolls_used = new_data['used']
                            folder.temp_roll_strategy = new_data['strategy']
                            folder.save(update_fields=[
                                'estimated_temp_rolls_created',
                                'estimated_temp_rolls_used',
                                'temp_roll_strategy'
                            ])

                    updated_count += 1
                    
                    if self.verbosity >= 1:
                        change_summary = []
                        if new_data['created'] != old_data['created']:
                            change_summary.append(f"created: {old_data['created']} → {new_data['created']}")
                        if new_data['used'] != old_data['used']:
                            change_summary.append(f"used: {old_data['used']} → {new_data['used']}")
                        if new_data['strategy'] != old_data['strategy']:
                            change_summary.append(f"strategy: {old_data['strategy']} → {new_data['strategy']}")
                        
                        action = "WOULD UPDATE" if dry_run else "UPDATED"
                        self.stdout.write(
                            self.style.SUCCESS(f"  {action}: {', '.join(change_summary)}")
                        )
                elif self.verbosity >= 2:
                    self.stdout.write("  No changes needed")

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ERROR processing folder {folder.id}: {str(e)}")
                )
                if self.verbosity >= 2:
                    logger.exception(f"Error processing analyzed folder {folder.id}")

        # Summary
        self.stdout.write("\n" + "="*50)
        action_verb = "would be updated" if dry_run else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"✓ {updated_count} folders {action_verb}")
        )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f"✗ {error_count} folders had errors")
            )

        skipped_count = total_folders - updated_count - error_count
        if skipped_count > 0:
            self.stdout.write(f"- {skipped_count} folders skipped (no changes needed)")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nThis was a dry run. Use --force to actually apply changes.")
            )
        else:
            self.stdout.write(f"\nTemp roll metrics update complete!")

    def _format_temp_roll_summary(self, temp_data):
        """Format temp roll data for display"""
        created = temp_data['temp_rolls_created']
        used = temp_data['temp_rolls_used']
        strategy = temp_data['strategy']
        
        parts = []
        if created > 0:
            parts.append(f"+{created} created")
        if used > 0:
            parts.append(f"{used} used")
        
        if parts:
            return f"{', '.join(parts)} ({strategy})"
        else:
            return f"none ({strategy})" 