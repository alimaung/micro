"""
Django management command to reanalyze existing analyzed folders with corrected logic.
This ensures all analyzed folders use the exact same logic as the register phase.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from microapp.models import AnalyzedFolder
from microapp.services import AnalyzeService
from pathlib import Path
import time


class Command(BaseCommand):
    help = 'Reanalyze existing analyzed folders with corrected register-phase-aligned logic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reanalyzed without actually doing it',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reanalysis even if folder was recently analyzed',
        )
        parser.add_argument(
            '--folder-path',
            type=str,
            help='Reanalyze specific folder path only',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of folders to process in each batch (default: 10)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting reanalysis of existing analyzed folders...')
        
        dry_run = options['dry_run']
        force = options['force']
        specific_folder = options['folder_path']
        batch_size = options['batch_size']
        
        # Get analyze service
        analyze_service = AnalyzeService()
        
        # Get a system user (or create one if needed)
        try:
            system_user = User.objects.filter(is_superuser=True).first()
            if not system_user:
                system_user = User.objects.filter(is_staff=True).first()
            if not system_user:
                self.stdout.write(
                    self.style.ERROR('No admin or staff user found. Please create one first.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error finding system user: {e}')
            )
            return
        
        # Build queryset
        if specific_folder:
            # Reanalyze specific folder
            analyzed_folders = AnalyzedFolder.objects.filter(folder_path=specific_folder)
            if not analyzed_folders.exists():
                self.stdout.write(
                    self.style.ERROR(f'No analyzed folder found for path: {specific_folder}')
                )
                return
        else:
            # Get all analyzed folders, ordered by analysis date
            analyzed_folders = AnalyzedFolder.objects.all().order_by('-analyzed_at')
        
        total_count = analyzed_folders.count()
        self.stdout.write(f'Found {total_count} analyzed folders to process')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual reanalysis will be performed'))
            for folder in analyzed_folders[:batch_size]:
                self.stdout.write(f'Would reanalyze: {folder.folder_path}')
                self.stdout.write(f'  Current stats: {folder.total_documents} docs, {folder.total_pages} pages, {folder.oversized_count} oversized')
                self.stdout.write(f'  Current rolls: {folder.estimated_rolls_16mm} x 16mm, {folder.estimated_rolls_35mm} x 35mm')
            return
        
        # Process folders in batches
        processed_count = 0
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f'Processing in batches of {batch_size}...')
        
        for i in range(0, total_count, batch_size):
            batch_folders = analyzed_folders[i:i + batch_size]
            
            self.stdout.write(f'\nProcessing batch {i//batch_size + 1}/{(total_count + batch_size - 1)//batch_size}')
            
            for folder in batch_folders:
                processed_count += 1
                
                try:
                    # Check if folder path exists
                    folder_path = Path(folder.folder_path)
                    if not folder_path.exists():
                        self.stdout.write(
                            self.style.ERROR(f'Folder does not exist: {folder.folder_path}')
                        )
                        error_count += 1
                        continue
                    
                    # Store original values for comparison
                    original_stats = {
                        'total_documents': folder.total_documents,
                        'total_pages': folder.total_pages,
                        'oversized_count': folder.oversized_count,
                        'has_oversized': folder.has_oversized,
                        'estimated_rolls_16mm': folder.estimated_rolls_16mm,
                        'estimated_rolls_35mm': folder.estimated_rolls_35mm,
                        'recommended_workflow': folder.recommended_workflow
                    }
                    
                    self.stdout.write(f'Reanalyzing: {folder.folder_path}')
                    self.stdout.write(f'  Original: {original_stats["total_documents"]} docs, {original_stats["total_pages"]} pages, {original_stats["oversized_count"]} oversized')
                    self.stdout.write(f'  Original rolls: {original_stats["estimated_rolls_16mm"]} x 16mm, {original_stats["estimated_rolls_35mm"]} x 35mm')
                    
                    # Perform reanalysis with force=True to override existing analysis
                    start_time = time.time()
                    result = analyze_service.analyze_folder_standalone(
                        folder_path=folder.folder_path,
                        user=system_user,
                        force_reanalyze=True
                    )
                    analysis_time = time.time() - start_time
                    
                    if result:
                        # The result is an AnalyzedFolder object, need to refresh it from DB to get updated values
                        folder.refresh_from_db()
                        
                        # Compare results
                        changes = []
                        
                        if folder.total_documents != original_stats['total_documents']:
                            changes.append(f"documents: {original_stats['total_documents']} → {folder.total_documents}")
                        
                        if folder.total_pages != original_stats['total_pages']:
                            changes.append(f"pages: {original_stats['total_pages']} → {folder.total_pages}")
                        
                        if folder.oversized_count != original_stats['oversized_count']:
                            changes.append(f"oversized: {original_stats['oversized_count']} → {folder.oversized_count}")
                        
                        if folder.estimated_rolls_16mm != original_stats['estimated_rolls_16mm']:
                            changes.append(f"16mm rolls: {original_stats['estimated_rolls_16mm']} → {folder.estimated_rolls_16mm}")
                        
                        if folder.estimated_rolls_35mm != original_stats['estimated_rolls_35mm']:
                            changes.append(f"35mm rolls: {original_stats['estimated_rolls_35mm']} → {folder.estimated_rolls_35mm}")
                        
                        if folder.recommended_workflow != original_stats['recommended_workflow']:
                            changes.append(f"workflow: {original_stats['recommended_workflow']} → {folder.recommended_workflow}")
                        
                        if changes:
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ Updated ({analysis_time:.2f}s): {", ".join(changes)}')
                            )
                            updated_count += 1
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ No changes needed ({analysis_time:.2f}s)')
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ Reanalysis failed')
                        )
                        error_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error reanalyzing {folder.folder_path}: {e}')
                    )
                    error_count += 1
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
            
            # Progress update
            self.stdout.write(f'Batch complete. Progress: {processed_count}/{total_count}')
        
        # Final summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('REANALYSIS COMPLETE'))
        self.stdout.write(f'Total processed: {processed_count}')
        self.stdout.write(f'Updated: {updated_count}')
        self.stdout.write(f'No changes: {processed_count - updated_count - error_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n{updated_count} folders were updated with corrected analysis logic!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No folders needed updates. All were already using correct logic.')
            ) 