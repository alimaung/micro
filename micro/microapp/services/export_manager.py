"""
Export Manager Module

This module provides services for exporting project data to the filesystem.
It handles processing localStorage objects from the frontend and saving them
in the appropriate project directory.
"""

import os
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
import zipfile
import shutil
from io import BytesIO

from django.conf import settings
from microapp.models import Project, ProcessedDocument

logger = logging.getLogger(__name__)

class ExportManager:
    """
    Manages the export process of project data, handling localStorage objects
    from frontend and saving them to appropriate directories.
    """

    def __init__(self):
        """Initialize the export manager."""
        self.logger = logger

    def export_project_data(self, project_id, data_dict):
        """
        Export project data received from frontend localStorage to the filesystem.

        Args:
            project_id (int): The ID of the project
            data_dict (dict): Dictionary containing the localStorage objects

        Returns:
            dict: Result of the export operation
        """
        try:
            # Get project info
            project = Project.objects.get(id=project_id)

            # Determine export directory from project state or create default
            export_dir = self._get_export_directory(project, data_dict)
            export_dir.mkdir(parents=True, exist_ok=True)

            # Export each localStorage object
            results = {}
            for key, data in data_dict.items():
                if not data:
                    continue
                
                # Skip keys that might contain sensitive information or are not needed
                if 'token' in key.lower() or 'password' in key.lower() or 'secret' in key.lower():
                    continue
                
                # Save data to file
                filename = f"{key}.json"
                file_path = export_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                results[key] = str(file_path)
                self.logger.info(f"Exported {key} to {file_path}")
            
            # Create additional export files
            additional_exports = self._generate_additional_exports(project, export_dir, data_dict)
            results.update(additional_exports)
            
            return {
                "status": "success",
                "message": f"Successfully exported project data to {export_dir}",
                "export_dir": str(export_dir),
                "exports": results
            }
        
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            return {
                "status": "error",
                "message": f"Project with ID {project_id} not found"
            }
        except Exception as e:
            self.logger.error(f"Error exporting project data: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Failed to export project data: {str(e)}"
            }

    def _get_export_directory(self, project, data_dict):
        """
        Determine the export directory based on project data.
        
        Args:
            project (Project): Project model instance
            data_dict (dict): Dictionary containing localStorage data
            
        Returns:
            Path: Path object for export directory
        """
        try:
            # Check if we have project state with destination path
            if 'microfilmProjectState' in data_dict and data_dict['microfilmProjectState']:
                project_state = data_dict['microfilmProjectState']
                
                if isinstance(project_state, str):
                    try:
                        project_state = json.loads(project_state)
                    except:
                        project_state = {}
                
                # Try to get destination path from project state
                if project_state.get('destinationPath'):
                    destination_path = Path(project_state['destinationPath'])
                    export_dir = destination_path / '.data'
                    return export_dir
            
            # Fallback - create in media directory
            archive_id = project.archive_id or f"project_{project.id}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path(settings.MEDIA_ROOT) / 'exports' / f"{archive_id}_{timestamp}"
            return export_dir
            
        except Exception as e:
            self.logger.error(f"Error determining export directory: {str(e)}")
            # Use default exports directory as fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return Path(settings.MEDIA_ROOT) / 'exports' / f"project_{project.id}_{timestamp}"

    def _generate_additional_exports(self, project, export_dir, data_dict):
        """
        Generate additional export files based on the localStorage data.
        
        Args:
            project (Project): Project model instance
            export_dir (Path): Export directory path
            data_dict (dict): Dictionary containing localStorage data
            
        Returns:
            dict: Dictionary mapping export names to file paths
        """
        results = {}
        
        try:
            # Generate index CSV file
            if 'microfilmFilmNumberResults' in data_dict and data_dict['microfilmFilmNumberResults']:
                index_csv_path = self._generate_index_csv(project, export_dir, data_dict)
                if index_csv_path:
                    results['index_csv'] = str(index_csv_path)
            
            # Generate project summary report
            summary_json_path = self._generate_project_summary(project, export_dir, data_dict)
            if summary_json_path:
                results['project_summary'] = str(summary_json_path)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error generating additional exports: {str(e)}")
            return results

    def _generate_index_csv(self, project, export_dir, data_dict):
        """
        Generate index CSV file from film number results.
        
        Args:
            project (Project): Project model instance
            export_dir (Path): Export directory path
            data_dict (dict): Dictionary containing localStorage data
            
        Returns:
            Path: Path to the generated CSV file
        """
        try:
            # Get film number data
            film_number_data = data_dict.get('microfilmFilmNumberResults')
            if not film_number_data:
                return None
                
            if isinstance(film_number_data, str):
                film_number_data = json.loads(film_number_data)
            
            # Generate CSV content
            csv_rows = ["Document ID,Film Number,Frame Start,Page Count,Document Type,Oversized"]
            
            # Extract document-film assignments
            assignments = film_number_data.get('assignments', [])
            for assignment in assignments:
                doc_id = assignment.get('documentId', '')
                film_number = assignment.get('filmNumber', '')
                frame_start = assignment.get('frameStart', '')
                page_count = assignment.get('pageCount', '')
                doc_type = assignment.get('documentType', 'PDF')
                oversized = assignment.get('hasOversized', False)
                
                csv_rows.append(f"{doc_id},{film_number},{frame_start},{page_count},{doc_type},{oversized}")
            
            # Write to file
            csv_path = export_dir / f"{project.archive_id or 'project'}_index.csv"
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(csv_rows))
            
            self.logger.info(f"Generated index CSV at {csv_path}")
            return csv_path
            
        except Exception as e:
            self.logger.error(f"Error generating index CSV: {str(e)}")
            return None

    def _generate_project_summary(self, project, export_dir, data_dict):
        """
        Generate project summary report from all localStorage data.
        
        Args:
            project (Project): Project model instance
            export_dir (Path): Export directory path
            data_dict (dict): Dictionary containing localStorage data
            
        Returns:
            Path: Path to the generated summary file
        """
        try:
            # Get key data from localStorage objects
            project_state = data_dict.get('microfilmProjectState', {})
            allocation_data = data_dict.get('microfilmAllocationData', {})
            film_number_data = data_dict.get('microfilmFilmNumberResults', {})
            distribution_data = data_dict.get('microfilmDistributionResults', {})
            
            # Convert string JSON to objects if needed
            if isinstance(project_state, str):
                project_state = json.loads(project_state)
            if isinstance(allocation_data, str):
                allocation_data = json.loads(allocation_data)
            if isinstance(film_number_data, str):
                film_number_data = json.loads(film_number_data)
            if isinstance(distribution_data, str):
                distribution_data = json.loads(distribution_data)
            
            # Extract project info
            project_info = project_state.get('projectInfo', {})
            archive_id = project_info.get('archiveId', project.archive_id)
            location = project_info.get('location', '')
            document_type = project_info.get('documentType', '')
            
            # Extract allocation info
            allocation_results = allocation_data.get('allocationResults', {})
            total_documents = allocation_results.get('documentCount', 0)
            total_pages = allocation_results.get('totalPages', 0)
            has_oversized = allocation_results.get('hasOversized', False)
            
            # Extract roll statistics
            rolls_data = allocation_data.get('rolls', {})
            roll_stats = {
                'rolls_16mm': len(rolls_data.get('rolls16mm', [])),
                'rolls_35mm': len(rolls_data.get('rolls35mm', [])),
                'total_rolls': len(rolls_data.get('rolls16mm', [])) + len(rolls_data.get('rolls35mm', []))
            }
            
            # Create summary object
            summary = {
                'project': {
                    'id': project.id,
                    'archive_id': archive_id,
                    'location': location,
                    'document_type': document_type,
                    'export_date': datetime.now().isoformat()
                },
                'statistics': {
                    'total_documents': total_documents,
                    'total_pages': total_pages,
                    'has_oversized': has_oversized,
                    'total_rolls': roll_stats['total_rolls'],
                    'rolls_16mm': roll_stats['rolls_16mm'],
                    'rolls_35mm': roll_stats['rolls_35mm']
                },
                'export_files': {
                    'project_state': 'microfilmProjectState.json',
                    'allocation_data': 'microfilmAllocationData.json',
                    'film_number_data': 'microfilmFilmNumberResults.json',
                    'distribution_results': 'microfilmDistributionResults.json',
                    'index_csv': f"{archive_id or 'project'}_index.csv"
                }
            }
            
            # Add distribution results if available
            if distribution_data and distribution_data.get('results'):
                dist_results = distribution_data.get('results', {})
                summary['distribution'] = {
                    'processed_count': dist_results.get('processed_count', 0),
                    'error_count': dist_results.get('error_count', 0),
                    'output_dir': dist_results.get('output_dir', ''),
                    'completion_time': dist_results.get('completion_time', '')
                }
            
            # Write to file
            summary_path = export_dir / f"{archive_id or 'project'}_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"Generated project summary at {summary_path}")
            return summary_path
            
        except Exception as e:
            self.logger.error(f"Error generating project summary: {str(e)}")
            return None

    def create_export_zip(self, project_id, export_dir=None):
        """
        Create a ZIP file containing all exports for the project.
        
        Args:
            project_id (int): The ID of the project
            export_dir (str, optional): Export directory path. If None, will try to find it.
            
        Returns:
            tuple: (zip_file_path, memory_file) or (None, None) on failure
        """
        try:
            project = Project.objects.get(id=project_id)
            
            # If export_dir not provided, try to find the latest export directory
            if not export_dir:
                archive_id = project.archive_id or f"project_{project.id}"
                exports_base = Path(settings.MEDIA_ROOT) / 'exports'
                
                # Find directories that match the project
                matching_dirs = [d for d in exports_base.glob(f"{archive_id}*") if d.is_dir()]
                if not matching_dirs:
                    self.logger.error(f"No export directory found for project {project_id}")
                    return None, None
                
                # Get the most recent export directory
                export_dir = str(max(matching_dirs, key=os.path.getctime))
            
            # Create ZIP filename
            archive_id = project.archive_id or f"project_{project.id}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{archive_id}_exports_{timestamp}.zip"
            zip_path = Path(export_dir) / zip_filename
            
            # Create ZIP file in memory
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from the export directory
                export_dir_path = Path(export_dir)
                for file_path in export_dir_path.glob('*'):
                    if file_path.is_file() and file_path.name != zip_filename:
                        zipf.write(file_path, arcname=file_path.name)
            
            # Save ZIP file to disk
            with open(zip_path, 'wb') as f:
                f.write(memory_file.getvalue())
            
            # Reset the memory file pointer
            memory_file.seek(0)
            
            self.logger.info(f"Created export ZIP at {zip_path}")
            return str(zip_path), memory_file
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            return None, None
        except Exception as e:
            self.logger.error(f"Error creating export ZIP: {str(e)}")
            return None, None
