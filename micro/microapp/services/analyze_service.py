"""
Analyze Service - Handles loading and processing of project analysis data
"""

import json
import os
import logging
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from ..models import Project, AnalyzedFolder

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
                    
                    # Count temp rolls created and used from roll data
                    temp_rolls_created = 0
                    temp_rolls_used = 0
                    temp_roll_strategy = 'none'
                    
                    # Analyze 16mm rolls for temp roll patterns
                    for roll in results.get('rolls_16mm', []):
                        if roll.get('created_temp_roll'):
                            temp_rolls_created += 1
                        if roll.get('source_temp_roll'):
                            temp_rolls_used += 1
                    
                    # Analyze 35mm rolls for temp roll patterns  
                    for roll in results.get('rolls_35mm', []):
                        if roll.get('created_temp_roll'):
                            temp_rolls_created += 1
                        if roll.get('source_temp_roll'):
                            temp_rolls_used += 1
                    
                    # Determine strategy
                    if temp_rolls_created > 0 and temp_rolls_used > 0:
                        temp_roll_strategy = 'both'
                    elif temp_rolls_created > 0:
                        temp_roll_strategy = 'create'
                    elif temp_rolls_used > 0:
                        temp_roll_strategy = 'use'
                    
                    summary.update({
                        'total_rolls_16mm': rolls_16mm,
                        'total_rolls_35mm': rolls_35mm,
                        'total_rolls': rolls_16mm + rolls_35mm,
                        'temp_rolls': temp_rolls,
                        'temp_rolls_created': temp_rolls_created,
                        'temp_rolls_used': temp_rolls_used,
                        'temp_roll_strategy': temp_roll_strategy
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
    
    def discover_unregistered_folders(self, base_path="X:\\"):
        """
        Discover folders that haven't been registered or analyzed yet.
        
        Args:
            base_path: Base directory to scan for potential projects (default X:)
            
        Returns:
            List of folder information for unregistered folders
        """
        unregistered_folders = []
        
        try:
            base_path_obj = Path(base_path)
            if not base_path_obj.exists():
                logger.warning(f"Base path does not exist: {base_path}")
                return unregistered_folders
            
            # Define exclusion patterns
            excluded_folders = {
                '.management',
                'tiftopdf',
                '$recycle.bin',
                'system volume information',
                'recycler'
            }
            
            # Get all subdirectories
            for folder_path in base_path_obj.iterdir():
                if not folder_path.is_dir():
                    continue
                
                folder_name = folder_path.name.lower()
                
                # Skip excluded folders
                if folder_name in excluded_folders:
                    continue
                
                # Skip folders starting with RRD9
                if folder_path.name.startswith('RRD9'):
                    continue
                
                # Skip hidden/system folders
                if folder_path.name.startswith('.') or folder_path.name.startswith('$'):
                    continue
                
                # Check if this folder is already registered (has .data folder)
                data_folder = folder_path / '.data'
                is_registered = data_folder.exists() and data_folder.is_dir()
                
                # Check if this folder is already analyzed
                # Normalize path to match what's stored in database
                folder_path_str = str(folder_path.resolve())
                
                # Try multiple path formats to handle database inconsistencies
                path_variants = [
                    folder_path_str,  # Normal: X:\folder
                    folder_path_str.replace('\\', '/'),  # Forward slashes: X:/folder
                    folder_path_str.replace(':\\', ':'),  # Missing backslash: X:folder
                ]
                
                # DEBUG: Print detailed path analysis
                print(f"=== DISCOVER DEBUG for {folder_path.name} ===")
                print(f"Raw folder_path: {folder_path}")
                print(f"Normalized folder_path_str: {folder_path_str}")
                print(f"Path variants to check: {path_variants}")
                print(f"Is registered (has .data): {is_registered}")
                
                # Check if analyzed using any path variant
                is_analyzed = AnalyzedFolder.objects.filter(
                    folder_path__in=path_variants
                ).exists()
                
                print(f"Is analyzed (DB lookup with variants): {is_analyzed}")
                
                # Check all analyzed folders to see what's in DB
                all_analyzed = AnalyzedFolder.objects.all()
                print(f"All analyzed folders in DB ({all_analyzed.count()}):")
                for af in all_analyzed:
                    print(f"  - {af.folder_name}: {af.folder_path}")
                    if folder_path.name.lower() == af.folder_name.lower():
                        print(f"    *** MATCH BY NAME: {af.folder_name}")
                        print(f"    *** DB path: '{af.folder_path}'")
                        print(f"    *** Check path: '{folder_path_str}'")
                        print(f"    *** Path in variants: {af.folder_path in path_variants}")
                
                print(f"Final decision - will include: {not is_registered and not is_analyzed}")
                print("=== END DEBUG ===\n")
                
                if not is_registered and not is_analyzed:
                    # Get basic folder info
                    folder_info = self._get_basic_folder_info(folder_path)
                    if folder_info:
                        unregistered_folders.append(folder_info)
                        
        except Exception as e:
            logger.error(f"Error discovering unregistered folders: {e}")
            
        return unregistered_folders
    
    def get_registered_projects_with_data(self):
        """
        Get all registered projects (those with .data folders) without filtering.
        
        Returns:
            List of projects with their analysis data
        """
        projects = Project.objects.all().order_by('-updated_at')
        projects_with_data = []
        
        for project in projects:
            project_data = self.get_project_summary_data(project)
            projects_with_data.append({
                'project': project,
                'data': project_data or {}
            })
        
        return projects_with_data
    
    def _get_basic_folder_info(self, folder_path):
        """
        Get basic information about a folder without full analysis.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            Dict with basic folder information including detailed file type counts
        """
        try:
            folder_path = Path(folder_path)
            
            # Count files and calculate size with detailed file type tracking
            file_count = 0
            total_size = 0
            pdf_count = 0
            excel_count = 0
            other_count = 0
            
            # Define Excel extensions
            excel_extensions = {'.xls', '.xlsx', '.xlsm', '.xlsb'}
            
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
                    
                    # Categorize file types
                    ext = file_path.suffix.lower()
                    if ext in {'.pdf'}:
                        pdf_count += 1
                    elif ext in excel_extensions:
                        excel_count += 1
                    else:
                        # Count other files (shortcuts, temp files, etc.)
                        other_count += 1
            
            return {
                'folder_path': str(folder_path.resolve()),  # Normalize path
                'folder_name': folder_path.name,
                'file_count': file_count,
                'total_size': total_size,
                'total_size_formatted': self.format_file_size(total_size),
                'pdf_count': pdf_count,
                'excel_count': excel_count,
                'other_count': other_count,
                'has_pdfs': pdf_count > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting basic folder info for {folder_path}: {e}")
            return None
    
    def analyze_folder_standalone(self, folder_path, user, force_reanalyze=False):
        """
        Analyze a folder without registering it as a project.
        
        Args:
            folder_path: Path to the folder to analyze
            user: User performing the analysis
            force_reanalyze: Whether to reanalyze if already analyzed
            
        Returns:
            AnalyzedFolder instance or None if analysis failed
        """
        try:
            # Normalize the folder path to ensure consistent comparison
            folder_path = str(Path(folder_path).resolve())
            
            # Check if already analyzed
            existing_analysis = AnalyzedFolder.objects.filter(folder_path=folder_path).first()
            if existing_analysis and not force_reanalyze:
                logger.info(f"Folder already analyzed: {folder_path}")
                return existing_analysis
            
            # Run the analysis (this would call your existing analysis logic)
            analysis_results = self._run_folder_analysis(folder_path)
            
            if not analysis_results:
                logger.error(f"Analysis failed for folder: {folder_path}")
                return None
            
            # Create or update AnalyzedFolder record
            analyzed_folder, created = AnalyzedFolder.objects.update_or_create(
                folder_path=folder_path,
                defaults={
                    'folder_name': Path(folder_path).name,
                    'total_documents': analysis_results.get('total_documents', 0),
                    'total_pages': analysis_results.get('total_pages', 0),
                    'oversized_count': analysis_results.get('oversized_count', 0),
                    'has_oversized': analysis_results.get('has_oversized', False),
                    'estimated_rolls_16mm': analysis_results.get('estimated_rolls_16mm', 0),
                    'estimated_rolls_35mm': analysis_results.get('estimated_rolls_35mm', 0),
                    'total_estimated_rolls': analysis_results.get('total_estimated_rolls', 0),
                    'estimated_temp_rolls_created': analysis_results.get('estimated_temp_rolls_created', 0),
                    'estimated_temp_rolls_used': analysis_results.get('estimated_temp_rolls_used', 0),
                    'temp_roll_strategy': analysis_results.get('temp_roll_strategy', 'unknown'),
                    'file_count': analysis_results.get('file_count', 0),
                    'total_size': analysis_results.get('total_size', 0),
                    'total_size_formatted': analysis_results.get('total_size_formatted', '0 B'),
                    'pdf_folder_found': analysis_results.get('pdf_folder_found', False),
                    'pdf_folder_path': analysis_results.get('pdf_folder_path'),
                    'analysis_data_path': analysis_results.get('analysis_data_path'),
                    'recommended_workflow': analysis_results.get('recommended_workflow', 'unknown'),
                    'analyzed_by': user
                }
            )
            
            logger.info(f"Successfully analyzed folder: {folder_path}")
            return analyzed_folder
            
        except Exception as e:
            logger.error(f"Error analyzing folder {folder_path}: {e}")
            return None
    
    def _run_folder_analysis(self, folder_path):
        """
        Run the actual analysis on a folder.
        This integrates with the existing document analysis logic.
        
        Args:
            folder_path: Path to analyze
            
        Returns:
            Dict with analysis results
        """
        try:
            folder_path = Path(folder_path)
            
            # Look for PDF folder first
            pdf_folder_path = None
            pdf_files = []
            
            # Check if there's a dedicated PDF subfolder
            for subfolder in folder_path.iterdir():
                if subfolder.is_dir():
                    pdf_count = len([f for f in subfolder.iterdir() 
                                   if f.is_file() and f.suffix.lower() == '.pdf'])
                    if pdf_count > 0:
                        # Use the first subfolder with PDFs as PDF folder
                        pdf_folder_path = str(subfolder)
                        pdf_files = [f for f in subfolder.iterdir() 
                                   if f.is_file() and f.suffix.lower() == '.pdf']
                        break
            
            # If no PDF subfolder found, look in root
            if not pdf_files:
                pdf_files = [f for f in folder_path.iterdir() 
                           if f.is_file() and f.suffix.lower() == '.pdf']
                if pdf_files:
                    pdf_folder_path = str(folder_path)
            
            if not pdf_files:
                # No PDFs found - return basic folder info
                file_count = len([f for f in folder_path.rglob('*') if f.is_file()])
                total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                
                return {
                    'total_documents': 0,
                    'total_pages': 0,
                    'oversized_count': 0,
                    'has_oversized': False,
                    'estimated_rolls_16mm': 0,
                    'estimated_rolls_35mm': 0,
                    'total_estimated_rolls': 0,
                    'file_count': file_count,
                    'total_size': total_size,
                    'total_size_formatted': self.format_file_size(total_size),
                    'pdf_folder_found': False,
                    'pdf_folder_path': None,
                    'analysis_data_path': None,
                    'recommended_workflow': 'no_documents'
                }
            
            # Perform actual document analysis
            analysis_results = self._analyze_pdf_documents(pdf_files, Path(pdf_folder_path))
            
            # Calculate roll estimates based on actual page counts and workflow
            total_pages = analysis_results['total_pages']
            has_oversized = analysis_results['has_oversized']
            
            # Use consistent capacities with allocation phase
            CAPACITY_16MM = 2940  # Pages per 16mm roll (matches allocation_views.py)
            CAPACITY_35MM = 690   # Pages per 35mm roll (matches allocation_views.py)
            
            if has_oversized:
                # Mixed workflow: 16mm for all pages + 35mm for oversized only
                estimated_rolls_16mm = max(1, (total_pages + CAPACITY_16MM - 1) // CAPACITY_16MM) if total_pages > 0 else 0
                
                # Estimate 35mm rolls using EXACT REGISTER PHASE LOGIC
                total_35mm_pages = 0
                for document in analysis_results['documents']:
                    if document.get('has_oversized', False):
                        # Count actual oversized pages in this document
                        total_oversized = document.get('total_oversized', 0)
                        
                        # If no count but we have the list, use its length
                        if total_oversized == 0 and 'oversized_pages' in document and document['oversized_pages']:
                            total_oversized = len(document['oversized_pages'])
                        
                        # Add reference pages (1:1 ratio as per register phase)
                        total_references = total_oversized
                        
                        # Total pages for this document in 35mm
                        document_35mm_pages = total_oversized + total_references
                        total_35mm_pages += document_35mm_pages
                
                # Calculate 35mm rolls needed
                estimated_rolls_35mm = max(1, (total_35mm_pages + CAPACITY_35MM - 1) // CAPACITY_35MM) if total_35mm_pages > 0 else 1
                
                recommended_workflow = 'hybrid'  # Requires both 16mm and 35mm
            else:
                # Standard workflow: 16mm only
                estimated_rolls_16mm = max(1, (total_pages + CAPACITY_16MM - 1) // CAPACITY_16MM) if total_pages > 0 else 0
                estimated_rolls_35mm = 0  # No 35mm needed for standard workflow
                recommended_workflow = 'standard_16mm'  # Can use 16mm only
            
            # Calculate temp roll estimates and strategy
            temp_roll_data = self._calculate_temp_roll_estimates(
                estimated_rolls_16mm, estimated_rolls_35mm, total_pages, has_oversized
            )
            
            # Calculate total folder size
            total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
            file_count = len([f for f in folder_path.rglob('*') if f.is_file()])
            
            return {
                'total_documents': analysis_results['document_count'],
                'total_pages': analysis_results['total_pages'],
                'oversized_count': analysis_results['oversized_count'],
                'has_oversized': analysis_results['has_oversized'],
                'estimated_rolls_16mm': estimated_rolls_16mm,
                'estimated_rolls_35mm': estimated_rolls_35mm,
                'total_estimated_rolls': estimated_rolls_16mm + estimated_rolls_35mm,
                'estimated_temp_rolls_created': temp_roll_data['temp_rolls_created'],
                'estimated_temp_rolls_used': temp_roll_data['temp_rolls_used'],
                'temp_roll_strategy': temp_roll_data['strategy'],
                'file_count': file_count,
                'total_size': total_size,
                'total_size_formatted': self.format_file_size(total_size),
                'pdf_folder_found': pdf_folder_path is not None,
                'pdf_folder_path': pdf_folder_path,
                'analysis_data_path': None,  # Would be set by actual analysis
                'recommended_workflow': recommended_workflow,
                'documents': analysis_results['documents']  # Detailed document info
            }
            
        except Exception as e:
            logger.error(f"Error running folder analysis: {e}")
            return None
    
    def _analyze_pdf_documents(self, pdf_files, pdf_folder_path):
        """
        Analyze PDF documents for page counts and oversized pages.
        Integrates with existing document analysis logic.
        
        Args:
            pdf_files: List of PDF file paths
            pdf_folder_path: Path to the PDF folder
            
        Returns:
            Dict with analysis results
        """
        import PyPDF2
        
        # Constants for oversized page detection (from document_views.py)
        OVERSIZE_THRESHOLD_WIDTH = 842  # A3 width in points
        OVERSIZE_THRESHOLD_HEIGHT = 1191  # A3 height in points
        
        results = {
            'document_count': 0,
            'total_pages': 0,
            'oversized_count': 0,  # Total oversized pages across all documents
            'documents_with_oversized': 0,  # Count of documents that have oversized pages
            'has_oversized': False,
            'documents': []
        }
        
        try:
            for pdf_file in pdf_files:
                if not pdf_file.suffix.lower() == '.pdf':
                    continue
                
                doc_result = {
                    'name': pdf_file.name,
                    'path': str(pdf_file),
                    'pages': 0,
                    'has_oversized': False,
                    'total_oversized': 0,
                    'oversized_pages': []
                }
                
                try:
                    # Read the PDF file
                    pdf_reader = PyPDF2.PdfReader(str(pdf_file))
                    page_count = len(pdf_reader.pages)
                    doc_result['pages'] = page_count
                    results['total_pages'] += page_count
                    
                    # Check each page for oversized dimensions
                    for i, page in enumerate(pdf_reader.pages):
                        try:
                            # Get page dimensions from mediabox
                            mediabox = page.mediabox
                            width, height = float(mediabox[2]), float(mediabox[3])
                            
                            # Check if page is oversized
                            is_oversized = ((width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
                                          (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH))
                            
                            if is_oversized:
                                doc_result['has_oversized'] = True
                                doc_result['total_oversized'] += 1
                                doc_result['oversized_pages'].append(i + 1)  # 1-based page number
                                results['has_oversized'] = True
                                results['oversized_count'] += 1  # Count each oversized page
                        except Exception as page_e:
                            # Skip problematic pages
                            logger.debug(f"Error analyzing page {i+1} in {pdf_file.name}: {page_e}")
                            continue
                    
                    # Count documents with oversized pages
                    if doc_result['has_oversized']:
                        results['documents_with_oversized'] += 1
                    
                    results['documents'].append(doc_result)
                    results['document_count'] += 1
                    
                except Exception as doc_e:
                    # Log error but continue with other documents
                    logger.warning(f"Error analyzing document {pdf_file.name}: {doc_e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error in PDF document analysis: {e}")
            return {
                'document_count': len(pdf_files),
                'total_pages': len(pdf_files) * 10,  # Fallback estimate
                'oversized_count': 0,
                'has_oversized': False,
                'documents': []
            }
    
    def get_analyzed_folders(self):
        """Get all analyzed folders that haven't been registered as projects"""
        from ..models import AnalyzedFolder
        return AnalyzedFolder.objects.filter(registered_as_project__isnull=True)
    
    def _calculate_temp_roll_estimates(self, estimated_rolls_16mm, estimated_rolls_35mm, total_pages, has_oversized):
        """
        Calculate estimated temp roll usage and creation based on project size and workflow.
        
        This method estimates temp roll behavior based on typical allocation patterns:
        - Small projects (1-2 rolls): Likely to create temp rolls with remaining capacity
        - Medium projects (3-5 rolls): May use existing temp rolls and create new ones
        - Large projects (6+ rolls): Likely to use existing temp rolls, create fewer new ones
        - Mixed workflow projects: Different patterns for 16mm vs 35mm
        
        Args:
            estimated_rolls_16mm: Number of 16mm rolls estimated
            estimated_rolls_35mm: Number of 35mm rolls estimated  
            total_pages: Total pages in the project
            has_oversized: Whether project has oversized documents
            
        Returns:
            Dict with temp roll estimates and strategy
        """
        temp_rolls_created = 0
        temp_rolls_used = 0
        strategy = 'none'
        
        total_rolls = estimated_rolls_16mm + estimated_rolls_35mm
        
        # Constants for capacity analysis
        CAPACITY_16MM = 2940
        CAPACITY_35MM = 690
        TEMP_ROLL_THRESHOLD = 200  # Minimum remaining capacity to create temp roll
        
        if total_rolls == 0:
            return {
                'temp_rolls_created': 0,
                'temp_rolls_used': 0,
                'strategy': 'none'
            }
        
        # Analyze 16mm temp roll patterns
        if estimated_rolls_16mm > 0:
            # Calculate if last 16mm roll would likely create a temp roll
            total_16mm_capacity = estimated_rolls_16mm * CAPACITY_16MM
            pages_for_16mm = total_pages  # 16mm gets all pages in both workflows
            last_roll_usage = pages_for_16mm % CAPACITY_16MM
            
            if last_roll_usage > 0:  # Not perfectly filled
                remaining_capacity = CAPACITY_16MM - last_roll_usage
                if remaining_capacity >= TEMP_ROLL_THRESHOLD:
                    temp_rolls_created += 1
        
        # Analyze 35mm temp roll patterns (only for mixed workflow)
        if estimated_rolls_35mm > 0 and has_oversized:
            # For 35mm, estimate based on oversized + reference pages
            # This is a simplified estimate since we don't have exact oversized page count here
            estimated_35mm_pages = total_pages * 0.1  # Rough estimate: 10% oversized
            estimated_35mm_pages_with_refs = estimated_35mm_pages * 2  # Add reference pages
            
            last_35mm_roll_usage = estimated_35mm_pages_with_refs % CAPACITY_35MM
            if last_35mm_roll_usage > 0:
                remaining_capacity = CAPACITY_35MM - last_35mm_roll_usage
                if remaining_capacity >= TEMP_ROLL_THRESHOLD:
                    temp_rolls_created += 1
        
        # Estimate temp roll usage based on project size
        if total_rolls >= 6:
            # Large projects likely to reuse existing temp rolls
            temp_rolls_used = min(2, total_rolls // 3)  # Use some existing temp rolls
            strategy = 'use' if temp_rolls_created == 0 else 'both'
        elif total_rolls >= 3:
            # Medium projects may use some existing temp rolls
            temp_rolls_used = min(1, total_rolls // 4)
            strategy = 'create' if temp_rolls_used == 0 else 'both'
        else:
            # Small projects primarily create temp rolls
            strategy = 'create' if temp_rolls_created > 0 else 'none'
        
        # Refine strategy based on final numbers
        if temp_rolls_created > 0 and temp_rolls_used > 0:
            strategy = 'both'
        elif temp_rolls_created > 0:
            strategy = 'create'
        elif temp_rolls_used > 0:
            strategy = 'use'
        else:
            strategy = 'none'
        
        return {
            'temp_rolls_created': temp_rolls_created,
            'temp_rolls_used': temp_rolls_used,
            'strategy': strategy
        }

    def register_analyzed_folder_as_project(self, analyzed_folder_id, project_data):
        """
        Convert an analyzed folder into a registered project.
        
        Args:
            analyzed_folder_id: ID of the AnalyzedFolder to register
            project_data: Dict with project registration data
            
        Returns:
            Project instance or None if registration failed
        """
        try:
            analyzed_folder = AnalyzedFolder.objects.get(id=analyzed_folder_id)
            
            if analyzed_folder.is_registered:
                logger.warning(f"Folder already registered: {analyzed_folder.folder_path}")
                return analyzed_folder.registered_as_project
            
            # Create new project - identical to regular registration flow
            # Use only the basic fields that regular registration uses
            project = Project.objects.create(
                archive_id=project_data.get('archive_id'),
                location=project_data.get('location'),
                doc_type=project_data.get('doc_type', ''),
                project_path=project_data.get('project_path'),
                project_folder_name=project_data.get('project_folder_name'),
                comlist_path=project_data.get('comlist_path'),
                output_dir=project_data.get('output_dir', ''),
                retain_sources=project_data.get('retain_sources', True),
                add_to_database=project_data.get('add_to_database', True),
                pdf_folder_path=project_data.get('pdf_folder_path', ''),
                has_pdf_folder=project_data.get('has_pdf_folder', False),
                owner=analyzed_folder.analyzed_by
            )
            
            # Link the analyzed folder to the project
            analyzed_folder.registered_as_project = project
            analyzed_folder.save()
            
            logger.info(f"Successfully registered analyzed folder as project: {project.archive_id}")
            return project
            
        except AnalyzedFolder.DoesNotExist:
            logger.error(f"AnalyzedFolder not found: {analyzed_folder_id}")
            return None
        except Exception as e:
            logger.error(f"Error registering analyzed folder as project: {e}")
            return None 