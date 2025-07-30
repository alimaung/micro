import os
from django.core.management.base import BaseCommand
from microapp.models import Project


class Command(BaseCommand):
    help = 'Fix COMList file paths that may have been incorrectly selected due to missing .xlsm support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Fix specific project ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get projects to check
        if project_id:
            projects = Project.objects.filter(id=project_id)
            if not projects.exists():
                self.stdout.write(self.style.ERROR(f'Project with ID {project_id} not found'))
                return
        else:
            projects = Project.objects.exclude(comlist_path__isnull=True).exclude(comlist_path='')
        
        self.stdout.write(f'Checking {projects.count()} projects...\n')
        
        fixed_count = 0
        potential_issues = 0
        
        for project in projects:
            self.stdout.write(f'Project {project.id} ({project.archive_id}):')
            self.stdout.write(f'  Current COMList: {project.comlist_path}')
            
            # Check if the current path exists
            if not os.path.exists(project.comlist_path):
                self.stdout.write(self.style.WARNING(f'  ⚠️  Current file does not exist'))
                potential_issues += 1
                continue
            
            # Get the directory containing the current COMList file
            comlist_dir = os.path.dirname(project.comlist_path)
            
            if not os.path.exists(comlist_dir):
                self.stdout.write(self.style.WARNING(f'  ⚠️  Directory does not exist'))
                potential_issues += 1
                continue
            
            # Find all Excel files in the directory
            excel_files = []
            try:
                for file in os.listdir(comlist_dir):
                    if file.lower().endswith(('.xlsx', '.xls', '.xlsm')):
                        excel_files.append(file)
            except PermissionError:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Permission denied accessing directory'))
                potential_issues += 1
                continue
            
            if not excel_files:
                self.stdout.write(f'  ℹ️  No Excel files found in directory')
                continue
            
            # Score each Excel file using the corrected algorithm
            scored_files = []
            for file in excel_files:
                score = self.score_comlist_file(file, project.archive_id)
                scored_files.append((file, score))
            
            # Sort by score (highest first)
            scored_files.sort(key=lambda x: x[1], reverse=True)
            
            self.stdout.write(f'  📊 Excel files found and scored:')
            for file, score in scored_files:
                current_marker = ' ← CURRENT' if file == os.path.basename(project.comlist_path) else ''
                self.stdout.write(f'    {file}: {score}{current_marker}')
            
            # Check if we should suggest a different file
            best_file, best_score = scored_files[0]
            current_file = os.path.basename(project.comlist_path)
            
            if best_file != current_file and best_score > self.score_comlist_file(current_file, project.archive_id):
                new_path = os.path.join(comlist_dir, best_file)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Better COMList file found: {best_file} (score: {best_score})'))
                
                if not dry_run:
                    project.comlist_path = new_path
                    project.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Updated COMList path to: {new_path}'))
                    fixed_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  📝 Would update to: {new_path}'))
            else:
                self.stdout.write(f'  ✅ Current file is already the best choice')
            
            self.stdout.write('')  # Empty line for readability
        
        # Summary
        self.stdout.write(self.style.SUCCESS('='*60))
        if dry_run:
            self.stdout.write(f'DRY RUN COMPLETE:')
            self.stdout.write(f'  Projects that would be fixed: {fixed_count}')
        else:
            self.stdout.write(f'OPERATION COMPLETE:')
            self.stdout.write(f'  Projects fixed: {fixed_count}')
        self.stdout.write(f'  Projects with potential issues: {potential_issues}')
    
    def score_comlist_file(self, filename, archive_id):
        """Score a COMList file candidate using the corrected algorithm"""
        extension = filename.split('.')[-1].lower()
        score = 0
        
        # Must be an Excel file to be considered
        if extension in ['xlsx', 'xls', 'xlsm']:
            score += 1
            
            # Contains comlist keyword
            if 'comlist' in filename.lower():
                score += 1
            
            # Contains archive ID
            if (filename == f'{archive_id}.xlsx' or 
                filename == f'{archive_id}.xls' or
                filename == f'{archive_id}.xlsm' or
                filename.startswith(f'{archive_id}_') or
                f'_{archive_id}' in filename):
                score += 1
            
            # Not in subfolder (this scoring assumes root folder, +1 always)
            score += 1
        
        return score 