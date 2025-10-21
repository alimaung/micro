"""
Django management command to discover missing export data in the directory/project structure.

This command checks each project for missing export data files, directories, and
identifies projects that may have incomplete export processes.

Usage:
    python manage.py discover_missing_export_data                    # Check all projects
    python manage.py discover_missing_export_data --project-id 123   # Check specific project
    python manage.py discover_missing_export_data --verbose          # Show detailed output
    python manage.py discover_missing_export_data --fix              # Attempt to fix missing directories
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Count, Q

from microapp.models import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Discover missing export data in the directory/project structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Check only the specified project ID',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output including file paths and sizes',
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Show only summary statistics, not individual project details',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix missing directories and create placeholder files',
        )
        parser.add_argument(
            '--check-register-state',
            action='store_true',
            help='Also check for missing register state data',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.summary_only = options['summary_only']
        self.fix_issues = options['fix']
        self.check_register_state = options['check_register_state']
        
        # Get projects to check
        if options['project_id']:
            try:
                projects = [Project.objects.get(id=options['project_id'])]
            except Project.DoesNotExist:
                raise CommandError(f'Project with ID {options["project_id"]} does not exist')
        else:
            projects = Project.objects.all().order_by('archive_id')
        
        if not projects:
            self.stdout.write(
                self.style.WARNING('No projects found')
            )
            return
        
        self.stdout.write(f'Checking {len(projects)} project(s) for missing export data...\n')
        
        # Initialize counters
        projects_with_issues = []
        total_projects = len(projects)
        projects_with_export_dirs = 0
        projects_with_register_state = 0
        projects_with_complete_exports = 0
        
        # Expected export data files ['microfilmReferenceSheets.json']
        expected_export_files = [
            'microfilmProjectState.json',
            'microfilmAnalysisData.json',
            'microfilmAllocationData.json',
            'microfilmFilmNumberResults.json',
            'microfilmDistributionResults.json',
            'microfilmIndexData.json',
            
        ]
        
        # Expected generated files (these are optional but good to have)
        expected_generated_files = [
            '_index.csv',
            '_summary.json'
        ]
        
        for project in projects:
            try:
                issues = self.check_project_export_data(
                    project, 
                    expected_export_files, 
                    expected_generated_files
                )
                
                if issues['has_export_dir']:
                    projects_with_export_dirs += 1
                
                if issues['has_register_state']:
                    projects_with_register_state += 1
                
                if issues['is_complete']:
                    projects_with_complete_exports += 1
                
                if issues['total_issues'] > 0:
                    projects_with_issues.append({
                        'project': project,
                        'issues': issues
                    })
                    
                    if not self.summary_only:
                        self.display_project_issues(project, issues)
                else:
                    if not self.summary_only:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Project {project.archive_id} (ID: {project.id}): '
                                f'Export data complete'
                            )
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Project {project.archive_id} (ID: {project.id}): Error - {str(e)}'
                    )
                )
                if self.verbose:
                    import traceback
                    self.stdout.write(traceback.format_exc())
        
        # Display summary
        self.display_summary(
            total_projects,
            projects_with_export_dirs,
            projects_with_register_state,
            projects_with_complete_exports,
            projects_with_issues
        )

    def check_project_export_data(self, project, expected_export_files, expected_generated_files):
        """
        Check a single project for missing export data.
        
        Args:
            project (Project): Project model instance
            expected_export_files (list): List of expected export file names
            expected_generated_files (list): List of expected generated file suffixes
            
        Returns:
            dict: Dictionary containing issue details
        """
        issues = {
            'has_export_dir': False,
            'has_register_state': False,
            'missing_export_files': [],
            'missing_generated_files': [],
            'export_directories': [],
            'register_state_files': [],
            'total_issues': 0,
            'is_complete': False
        }
        
        archive_id = project.archive_id or f"project_{project.id}"
        
        # Check for export directories
        export_dirs = self.find_export_directories(project)
        issues['export_directories'] = export_dirs
        issues['has_export_dir'] = len(export_dirs) > 0
        
        # Check each export directory for missing files
        if export_dirs:
            for export_dir in export_dirs:
                missing_files = self.check_export_directory(
                    export_dir, 
                    expected_export_files, 
                    expected_generated_files,
                    archive_id
                )
                issues['missing_export_files'].extend(missing_files['export_files'])
                issues['missing_generated_files'].extend(missing_files['generated_files'])
        else:
            # No export directory found - all files are missing
            issues['missing_export_files'] = expected_export_files.copy()
            issues['missing_generated_files'] = [f"{archive_id}{suffix}" for suffix in expected_generated_files]
        
        # Check for register state data if requested
        if self.check_register_state:
            register_state_files = self.check_register_state_data(project)
            issues['register_state_files'] = register_state_files
            issues['has_register_state'] = len(register_state_files) > 0
        
        # Calculate total issues
        issues['total_issues'] = (
            len(issues['missing_export_files']) + 
            len(issues['missing_generated_files']) +
            (0 if issues['has_export_dir'] else 1) +
            (0 if not self.check_register_state or issues['has_register_state'] else 1)
        )
        
        # Determine if export is complete
        issues['is_complete'] = (
            issues['has_export_dir'] and 
            len(issues['missing_export_files']) == 0 and
            (not self.check_register_state or issues['has_register_state'])
        )
        
        # Fix issues if requested
        if self.fix_issues and issues['total_issues'] > 0:
            self.fix_project_issues(project, issues)
        
        return issues

    def find_export_directories(self, project):
        """
        Find all export directories for a project.
        
        Args:
            project (Project): Project model instance
            
        Returns:
            list: List of Path objects for export directories
        """
        export_dirs = []
        archive_id = project.archive_id or f"project_{project.id}"
        
        # Check in MEDIA_ROOT/exports/
        exports_base = Path(settings.MEDIA_ROOT) / 'exports'
        if exports_base.exists():
            # Find directories that match the project
            matching_dirs = [d for d in exports_base.glob(f"{archive_id}*") if d.is_dir()]
            export_dirs.extend(matching_dirs)
        
        # Check for .data directory in project path (most common location)
        if project.project_path:
            project_path = Path(project.project_path)
            if project_path.exists():
                data_dir = project_path / '.data'
                if data_dir.exists():
                    export_dirs.append(data_dir)
        
        # Check in project's output directory if specified
        if project.output_dir:
            output_path = Path(project.output_dir)
            if output_path.exists():
                # Look for .data subdirectory
                data_dir = output_path / '.data'
                if data_dir.exists():
                    export_dirs.append(data_dir)
        
        # Check in project's data directory if specified
        if project.data_dir:
            data_path = Path(project.data_dir)
            if data_path.exists():
                export_dirs.append(data_path)
        
        # Check in MEDIA_ROOT/register_state/<project_id>/ (alternative location)
        register_state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project.id)
        if register_state_dir.exists():
            export_dirs.append(register_state_dir)
        
        return export_dirs

    def check_export_directory(self, export_dir, expected_export_files, expected_generated_files, archive_id):
        """
        Check an export directory for missing files.
        
        Args:
            export_dir (Path): Path to export directory
            expected_export_files (list): List of expected export file names
            expected_generated_files (list): List of expected generated file suffixes
            archive_id (str): Archive ID for generated files
            
        Returns:
            dict: Dictionary with missing files
        """
        missing_files = {
            'export_files': [],
            'generated_files': []
        }
        
        if not export_dir.exists():
            missing_files['export_files'] = expected_export_files.copy()
            missing_files['generated_files'] = [f"{archive_id}{suffix}" for suffix in expected_generated_files]
            return missing_files
        
        # Check for export files
        for filename in expected_export_files:
            file_path = export_dir / filename
            if not file_path.exists():
                missing_files['export_files'].append(filename)
        
        # Check for generated files
        for suffix in expected_generated_files:
            expected_filename = f"{archive_id}{suffix}"
            file_path = export_dir / expected_filename
            if not file_path.exists():
                missing_files['generated_files'].append(expected_filename)
        
        return missing_files

    def check_register_state_data(self, project):
        """
        Check for register state data files.
        
        Args:
            project (Project): Project model instance
            
        Returns:
            list: List of found register state files
        """
        register_state_files = []
        
        # Check in MEDIA_ROOT/register_state/<project_id>/
        state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project.id)
        if state_dir.exists():
            for file_path in state_dir.glob('*.json'):
                register_state_files.append(file_path.name)
        
        return register_state_files

    def display_project_issues(self, project, issues):
        """
        Display issues for a single project.
        
        Args:
            project (Project): Project model instance
            issues (dict): Issues dictionary
        """
        self.stdout.write(
            self.style.ERROR(
                f'✗ Project {project.archive_id} (ID: {project.id}): '
                f'{issues["total_issues"]} issue(s) found'
            )
        )
        
        if self.verbose:
            # Show export directories
            if issues['export_directories']:
                self.stdout.write(f'    Export directories found:')
                for export_dir in issues['export_directories']:
                    self.stdout.write(f'      - {export_dir}')
            else:
                self.stdout.write(f'    ⚠ No export directories found')
            
            # Show missing export files
            if issues['missing_export_files']:
                self.stdout.write(f'    Missing export files:')
                for filename in issues['missing_export_files']:
                    self.stdout.write(f'      - {filename}')
            
            # Show missing generated files
            if issues['missing_generated_files']:
                self.stdout.write(f'    Missing generated files:')
                for filename in issues['missing_generated_files']:
                    self.stdout.write(f'      - {filename}')
            
            # Show register state info
            if self.check_register_state:
                if issues['register_state_files']:
                    self.stdout.write(f'    Register state files found:')
                    for filename in issues['register_state_files']:
                        self.stdout.write(f'      - {filename}')
                else:
                    self.stdout.write(f'    ⚠ No register state files found')

    def fix_project_issues(self, project, issues):
        """
        Attempt to fix issues for a project.
        
        Args:
            project (Project): Project model instance
            issues (dict): Issues dictionary
        """
        try:
            archive_id = project.archive_id or f"project_{project.id}"
            
            # Create export directory if missing
            if not issues['has_export_dir']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_dir = Path(settings.MEDIA_ROOT) / 'exports' / f"{archive_id}_{timestamp}"
                export_dir.mkdir(parents=True, exist_ok=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Created export directory: {export_dir}')
                )
                
                # Create placeholder files
                for filename in issues['missing_export_files']:
                    placeholder_path = export_dir / filename
                    with open(placeholder_path, 'w') as f:
                        json.dump({
                            "status": "placeholder",
                            "message": f"Placeholder file created by discover_missing_export_data command",
                            "created_at": datetime.now().isoformat(),
                            "project_id": project.id,
                            "archive_id": archive_id
                        }, f, indent=2)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✓ Created placeholder: {filename}')
                    )
            
            # Create register state directory if missing and requested
            if self.check_register_state and not issues['has_register_state']:
                state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project.id)
                state_dir.mkdir(parents=True, exist_ok=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Created register state directory: {state_dir}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'    ✗ Error fixing issues: {str(e)}')
            )

    def display_summary(self, total_projects, projects_with_export_dirs, 
                       projects_with_register_state, projects_with_complete_exports, 
                       projects_with_issues):
        """
        Display summary statistics.
        """
        self.stdout.write('\n' + '='*60)
        self.stdout.write('EXPORT DATA DISCOVERY SUMMARY:')
        self.stdout.write(f'  Total projects checked: {total_projects}')
        self.stdout.write(f'  Projects with export directories: {projects_with_export_dirs}')
        
        if self.check_register_state:
            self.stdout.write(f'  Projects with register state data: {projects_with_register_state}')
        
        self.stdout.write(f'  Projects with complete exports: {projects_with_complete_exports}')
        self.stdout.write(f'  Projects with issues: {len(projects_with_issues)}')
        
        if total_projects > 0:
            completion_rate = (projects_with_complete_exports / total_projects) * 100
            self.stdout.write(f'  Export completion rate: {completion_rate:.1f}%')
        
        # List projects with issues
        if projects_with_issues:
            self.stdout.write(f'\nPROJECTS WITH EXPORT ISSUES:')
            for item in projects_with_issues:
                project = item['project']
                issues = item['issues']
                
                issue_summary = []
                if not issues['has_export_dir']:
                    issue_summary.append('no export dir')
                if issues['missing_export_files']:
                    issue_summary.append(f'{len(issues["missing_export_files"])} missing files')
                if issues['missing_generated_files']:
                    issue_summary.append(f'{len(issues["missing_generated_files"])} missing generated')
                if self.check_register_state and not issues['has_register_state']:
                    issue_summary.append('no register state')
                
                self.stdout.write(
                    f'  - {project.archive_id} (ID: {project.id}): '
                    f'{", ".join(issue_summary)}'
                )
        else:
            self.stdout.write(f'\n{self.style.SUCCESS("✓ All projects have complete export data!")}')
        
        # Show fix summary if fixes were applied
        if self.fix_issues:
            self.stdout.write(f'\nFIX SUMMARY:')
            self.stdout.write(f'  Attempted to fix issues for {len(projects_with_issues)} projects')
            self.stdout.write(f'  Check the output above for specific fix results')
