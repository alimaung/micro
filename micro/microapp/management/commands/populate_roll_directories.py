"""
Management command to populate output_directory field for existing rolls.

This command scans existing projects and rolls to find their distributed document
directories and updates the Roll model with the correct output_directory paths.
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from microapp.models import Project, Roll


class Command(BaseCommand):
    help = 'Populate output_directory field for existing rolls based on distributed documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Only process rolls for a specific project ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update rolls even if they already have output_directory set',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        project_id = options.get('project_id')

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Get projects to process
        if project_id:
            try:
                projects = [Project.objects.get(id=project_id)]
                self.stdout.write(f"Processing project ID: {project_id}")
            except Project.DoesNotExist:
                raise CommandError(f'Project with ID {project_id} does not exist')
        else:
            projects = Project.objects.filter(distribution_complete=True)
            self.stdout.write(f"Processing {projects.count()} projects with completed distribution")

        total_updated = 0
        total_found = 0
        total_missing = 0

        for project in projects:
            self.stdout.write(f"\nProcessing project: {project.archive_id}")
            
            # Get the expected output directory for this project
            project_output_dir = Path(project.project_path) / ".output"
            
            if not project_output_dir.exists():
                self.stdout.write(
                    self.style.WARNING(f"  Output directory not found: {project_output_dir}")
                )
                continue

            # Get rolls for this project
            rolls_query = project.rolls.all()
            if not self.force:
                rolls_query = rolls_query.filter(output_directory__isnull=True)

            rolls = rolls_query.filter(film_number__isnull=False)
            
            if not rolls.exists():
                self.stdout.write("  No rolls to process")
                continue

            self.stdout.write(f"  Found {rolls.count()} rolls to process")

            for roll in rolls:
                result = self._process_roll(roll, project_output_dir)
                if result == 'updated':
                    total_updated += 1
                elif result == 'found':
                    total_found += 1
                elif result == 'missing':
                    total_missing += 1

        # Summary
        self.stdout.write(f"\n{self.style.SUCCESS('Summary:')}")
        self.stdout.write(f"  Rolls updated: {total_updated}")
        self.stdout.write(f"  Rolls with existing directories: {total_found}")
        self.stdout.write(f"  Rolls with missing directories: {total_missing}")

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('\nDRY RUN - No actual changes were made')
            )

    def _process_roll(self, roll, project_output_dir):
        """
        Process a single roll to find and set its output directory.
        
        Returns:
            'updated' - Roll was updated with directory path
            'found' - Roll already had correct directory path
            'missing' - Roll directory not found
        """
        # Expected roll directory path
        expected_roll_dir = project_output_dir / roll.film_number
        
        # Check if directory exists
        if not expected_roll_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"    Roll {roll.film_number}: Directory not found - {expected_roll_dir}")
            )
            return 'missing'

        # Check if roll already has the correct path
        current_path = roll.output_directory
        expected_path_str = str(expected_roll_dir)

        if current_path == expected_path_str:
            self.stdout.write(f"    Roll {roll.film_number}: Already has correct path")
            return 'found'

        # Update the roll
        if not self.dry_run:
            with transaction.atomic():
                roll.output_directory = expected_path_str
                roll.save(update_fields=['output_directory'])

        if current_path:
            self.stdout.write(
                self.style.SUCCESS(
                    f"    Roll {roll.film_number}: Updated path from '{current_path}' to '{expected_path_str}'"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"    Roll {roll.film_number}: Set path to '{expected_path_str}'"
                )
            )

        return 'updated' 