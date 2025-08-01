"""
Django management command to fix path inconsistencies in AnalyzedFolder table
"""

from django.core.management.base import BaseCommand
from microapp.models import AnalyzedFolder
from pathlib import Path


class Command(BaseCommand):
    help = 'Fix path inconsistencies in AnalyzedFolder table'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix AnalyzedFolder paths...')
        
        analyzed_folders = AnalyzedFolder.objects.all()
        fixed_count = 0
        
        for folder in analyzed_folders:
            original_path = folder.folder_path
            
            # Try to normalize the path
            try:
                # Handle the missing backslash issue: X:folder -> X:\folder
                if ':' in original_path and '\\' not in original_path and '/' not in original_path:
                    # This looks like X:foldername, fix it to X:\foldername
                    drive_letter = original_path.split(':')[0]
                    folder_name = original_path.split(':')[1]
                    corrected_path = f"{drive_letter}:\\{folder_name}"
                    
                    self.stdout.write(f"Fixing: '{original_path}' -> '{corrected_path}'")
                    
                    folder.folder_path = corrected_path
                    folder.save()
                    fixed_count += 1
                else:
                    # Path looks normal, just normalize it
                    normalized_path = str(Path(original_path).resolve())
                    if normalized_path != original_path:
                        self.stdout.write(f"Normalizing: '{original_path}' -> '{normalized_path}'")
                        folder.folder_path = normalized_path
                        folder.save()
                        fixed_count += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error fixing path '{original_path}': {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {fixed_count} folder paths')
        ) 