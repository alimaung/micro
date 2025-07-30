"""
Analyze Service - Handles loading and processing of project analysis data
"""

import json
import os
import logging
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from ..models import Project

logger = logging.getLogger(__name__)

class AnalyzeService:
    """Service for loading and processing project analysis data"""
    
    def __init__(self):
        self.data_dir = Path(settings.BASE_DIR).parent / '.data'
        self.cache_timeout = 300  # 5 minutes
    
    def get_data_file_path(self, filename):
        """Get the full path to a data file"""
        return self.data_dir / filename
    
    def load_json_file(self, filename):
        """Load a JSON file with caching"""
        cache_key = f"analyze_data_{filename}"
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        file_path = self.get_data_file_path(filename)
        
        if not file_path.exists():
            logger.warning(f"Data file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cache.set(cache_key, data, self.cache_timeout)
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file {filename}: {e}")
            return None
    
    def get_project_analysis_data(self, project_id):
        """Get analysis data for a specific project"""
        # Check if project has a data_dir or use project ID
        try:
            project = Project.objects.get(id=project_id)
            if project.data_dir:
                # Use project-specific data directory
                data_dir = Path(project.data_dir)
            else:
                data_dir = self.data_dir
        except Project.DoesNotExist:
            data_dir = self.data_dir
        
        analysis_data = {}
        
        # Load main data files
        files_to_load = [
            'microfilmProjectState.json',
            'microfilmAnalysisData.json',
            'microfilmAllocationData.json',
            'microfilmIndexData.json',
            'microfilmFilmNumberResults.json'
        ]
        
        for filename in files_to_load:
            file_path = data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    key = filename.replace('microfilm', '').replace('.json', '').lower()
                    analysis_data[key] = data
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
        
        return analysis_data
    
    def get_projects_with_analysis_data(self):
        """Get all projects that have analysis data and filter by status"""
        projects = Project.objects.all().order_by('-updated_at')
        projects_with_data = []
        
        for project in projects:
            # Filter out projects that have moved beyond register step
            if (project.processing_complete or 
                project.film_allocation_complete or 
                project.distribution_complete or 
                project.handoff_complete):
                continue
            
            project_data = self.get_project_summary_data(project)
            if project_data:
                projects_with_data.append({
                    'project': project,
                    'data': project_data
                })
        
        return projects_with_data
    
    def get_project_summary_data(self, project):
        """Get summary data for a project card"""
        try:
            data = self.get_project_analysis_data(project.id)
            
            if not data:
                return None
            
            summary = {
                'project_id': project.id,
                'archive_id': project.archive_id,
                'location': project.location,
                'doc_type': project.doc_type,
                'created_at': project.created_at,
                'updated_at': project.updated_at
            }
            
            # Extract key metrics from analysis data
            if 'analysisdata' in data:
                analysis = data['analysisdata'].get('analysisResults', {})
                summary.update({
                    'total_documents': analysis.get('documentCount', 0),
                    'total_pages': analysis.get('pageCount', 0),
                    'oversized_count': analysis.get('oversizedCount', 0),
                    'has_oversized': analysis.get('hasOversized', False),
                    'total_references': analysis.get('totalReferences', 0),
                    'workflow': analysis.get('recommendedWorkflow', 'unknown')
                })
            
            # Extract allocation data
            if 'allocationdata' in data:
                allocation = data['allocationdata'].get('allocationResults', {})
                if 'results' in allocation:
                    results = allocation['results']
                    rolls_16mm = len(results.get('rolls_16mm', []))
                    rolls_35mm = len(results.get('rolls_35mm', []))
                    temp_rolls = len(results.get('temp_rolls', []))
                    summary.update({
                        'total_rolls_16mm': rolls_16mm,
                        'total_rolls_35mm': rolls_35mm,
                        'total_rolls': rolls_16mm + rolls_35mm,
                        'temp_rolls': temp_rolls
                    })
            
            # Extract project state data
            if 'projectstatedata' in data:
                project_state = data['projectstatedata']
                if 'sourceData' in project_state:
                    source_data = project_state['sourceData']
                    summary.update({
                        'file_count': source_data.get('fileCount', 0),
                        'total_size': source_data.get('totalSize', 0),
                        'total_size_formatted': source_data.get('totalSizeFormatted', '0 MB'),
                        'source_path': source_data.get('path', '')
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting summary data for project {project.id}: {e}")
            return None
    
    def calculate_directory_size(self, path):
        """Calculate the total size of a directory"""
        try:
            total_size = 0
            path_obj = Path(path)
            
            if not path_obj.exists():
                return 0
            
            for file_path in path_obj.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
        except Exception as e:
            logger.error(f"Error calculating directory size for {path}: {e}")
            return 0
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}" 