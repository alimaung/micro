"""
Django management command to find all projects with missing COM IDs.

This command checks each project's documents and identifies projects that have
documents without COM IDs assigned.

Usage:
    python manage.py find_missing_com_ids                    # Check all projects
    python manage.py find_missing_com_ids --project-id 123   # Check specific project
    python manage.py find_missing_com_ids --verbose          # Show detailed output
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from microapp.models import Project, Document


class Command(BaseCommand):
    help = 'Find all projects with missing COM IDs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Check only the specified project ID',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output including document counts',
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Show only summary statistics, not individual project details',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.summary_only = options['summary_only']
        
        # Get projects to check
        if options['project_id']:
            try:
                projects = [Project.objects.get(id=options['project_id'])]
            except Project.DoesNotExist:
                raise CommandError(f'Project with ID {options["project_id"]} does not exist')
        else:
            projects = Project.objects.all()
        
        if not projects:
            self.stdout.write(
                self.style.WARNING('No projects found')
            )
            return
        
        self.stdout.write(f'Checking {len(projects)} project(s) for missing COM IDs...\n')
        
        projects_with_missing_com_ids = []
        total_documents = 0
        total_documents_with_com_ids = 0
        total_documents_without_com_ids = 0
        
        for project in projects:
            try:
                # Get document statistics for this project
                doc_stats = self.get_project_document_stats(project)
                
                if doc_stats['total_documents'] == 0:
                    if self.verbose:
                        self.stdout.write(f'  Project {project.archive_id} (ID: {project.id}): No documents')
                    continue
                
                total_documents += doc_stats['total_documents']
                total_documents_with_com_ids += doc_stats['documents_with_com_ids']
                total_documents_without_com_ids += doc_stats['documents_without_com_ids']
                
                # Check if this project has missing COM IDs
                if doc_stats['documents_without_com_ids'] > 0:
                    projects_with_missing_com_ids.append({
                        'project': project,
                        'stats': doc_stats
                    })
                    
                    if not self.summary_only:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Project {project.archive_id} (ID: {project.id}): '
                                f'{doc_stats["documents_without_com_ids"]}/{doc_stats["total_documents"]} '
                                f'documents missing COM IDs'
                            )
                        )
                        
                        if self.verbose:
                            self.stdout.write(f'    - Documents with COM IDs: {doc_stats["documents_with_com_ids"]}')
                            self.stdout.write(f'    - Documents without COM IDs: {doc_stats["documents_without_com_ids"]}')
                            self.stdout.write(f'    - Completion rate: {(doc_stats["documents_with_com_ids"] / doc_stats["total_documents"] * 100):.1f}%')
                else:
                    if not self.summary_only:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Project {project.archive_id} (ID: {project.id}): '
                                f'All {doc_stats["total_documents"]} documents have COM IDs'
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
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'SUMMARY:')
        self.stdout.write(f'  Total projects checked: {len(projects)}')
        self.stdout.write(f'  Projects with missing COM IDs: {len(projects_with_missing_com_ids)}')
        self.stdout.write(f'  Total documents: {total_documents}')
        self.stdout.write(f'  Documents with COM IDs: {total_documents_with_com_ids}')
        self.stdout.write(f'  Documents without COM IDs: {total_documents_without_com_ids}')
        
        if total_documents > 0:
            completion_rate = (total_documents_with_com_ids / total_documents) * 100
            self.stdout.write(f'  Overall completion rate: {completion_rate:.1f}%')
        
        # List projects with missing COM IDs
        if projects_with_missing_com_ids:
            self.stdout.write(f'\nPROJECTS WITH MISSING COM IDs:')
            for item in projects_with_missing_com_ids:
                project = item['project']
                stats = item['stats']
                completion_rate = (stats['documents_with_com_ids'] / stats['total_documents']) * 100
                
                self.stdout.write(
                    f'  - {project.archive_id} (ID: {project.id}): '
                    f'{stats["documents_without_com_ids"]}/{stats["total_documents"]} missing '
                    f'({completion_rate:.1f}% complete)'
                )
        else:
            self.stdout.write(f'\n{self.style.SUCCESS("✓ All projects have complete COM ID assignments!")}')

    def get_project_document_stats(self, project):
        """Get document statistics for a project."""
        
        # Get total documents for this project
        total_documents = Document.objects.filter(project=project).count()
        
        if total_documents == 0:
            return {
                'total_documents': 0,
                'documents_with_com_ids': 0,
                'documents_without_com_ids': 0
            }
        
        # Get documents with COM IDs (not None and not empty string)
        documents_with_com_ids = Document.objects.filter(
            project=project,
            com_id__isnull=False
        ).exclude(com_id='').count()
        
        # Get documents without COM IDs
        documents_without_com_ids = Document.objects.filter(
            project=project
        ).filter(
            Q(com_id__isnull=True) | Q(com_id='')
        ).count()
        
        return {
            'total_documents': total_documents,
            'documents_with_com_ids': documents_with_com_ids,
            'documents_without_com_ids': documents_without_com_ids
        }


