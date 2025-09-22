"""
Analysis-only version of the microfilm processing system.

This module provides a SAFE analysis mode that processes projects from X: drive
without modifying any production data. All outputs are redirected to AnalysisResults.
"""

import sys
import os
import argparse
from pathlib import Path
import json
import shutil
from typing import List, Dict, Any
from tqdm import tqdm
from datetime import datetime

# Microfilm modules
from logger import FilmLogger, LogLevel
from models import Project
from project_service import ProjectService
from document_service import DocumentProcessingService
from distribution_service import DocumentDistributionService
from film_service import FilmService
from index_service import IndexService
from film_number_service import FilmNumberService
from export_service import ExportService
from reference_service import ReferenceSheetService


class TqdmLoggerWrapper:
    """
    Wrapper to ensure all logger output goes through tqdm.write() 
    to prevent interference with progress bars.
    """
    def __init__(self, original_logger):
        self.original_logger = original_logger
        # Store original _log method
        self._original_log = original_logger._log
        # Replace with tqdm-aware version
        original_logger._log = self._tqdm_log
    
    def _tqdm_log(self, module, level, message, extras=None):
        """
        Override _log to use tqdm.write for console output
        """
        if level < self.original_logger.log_level:
            return
        
        console_msg, file_msg = self.original_logger._format_message(module, level, message, extras)
        
        # Use tqdm.write for console output to work with progress bars
        tqdm.write(console_msg)
        
        # Write to file if file handler exists
        if hasattr(self.original_logger, 'file_handler') and self.original_logger.file_handler:
            print(file_msg, file=self.original_logger.file_handler)
    
    def restore(self):
        """Restore original logging behavior"""
        self.original_logger._log = self._original_log


class AnalysisProjectService(ProjectService):
    """
    Analysis-only version of ProjectService that redirects all outputs to AnalysisResults.
    """
    
    def __init__(self, analysis_base_dir: Path, logger=None):
        super().__init__(logger)
        self.analysis_base_dir = analysis_base_dir
        self.analysis_base_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_project_for_analysis(self, production_path: Path) -> Project:
        """
        Initialize a project for analysis mode, redirecting all paths to AnalysisResults.
        """
        # First, initialize the project normally to extract metadata
        original_project = self.initialize_project(production_path)
        
        # Create analysis directory structure
        analysis_project_dir = self.analysis_base_dir / original_project.project_folder_name
        analysis_project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .data directory in analysis location
        analysis_data_dir = analysis_project_dir / ".data"
        analysis_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a new project with redirected paths
        analysis_project = Project(
            archive_id=original_project.archive_id,
            location=original_project.location,
            project_path=analysis_project_dir,  # Redirected to AnalysisResults
            project_folder_name=original_project.project_folder_name,
            document_folder_path=original_project.document_folder_path,  # Keep original for reading
            document_folder_name=original_project.document_folder_name,
            doc_type=original_project.doc_type,
            comlist_path=original_project.comlist_path,  # Keep original for reading
            output_dir=analysis_data_dir  # Redirect output to analysis location
        )
        
        # Store reference to original production path for reading documents
        analysis_project._original_production_path = production_path
        
        return analysis_project

class AnalysisFilmNumberService(FilmNumberService):
    """
    Analysis-only version that uses a separate database in AnalysisResults.
    """
    
    def __init__(self, analysis_base_dir: Path, logger=None):
        # Use analysis database path
        analysis_db_path = analysis_base_dir / "analysis_film_allocation.sqlite3"
        super().__init__(db_path=str(analysis_db_path), logger=logger)

class AnalysisDistributionService(DocumentDistributionService):
    """
    Analysis-only distribution service that prevents file operations in production.
    """
    
    def __init__(self, analysis_base_dir: Path, logger=None, film_number_service=None, reference_service=None):
        super().__init__(logger, film_number_service, reference_service)
        self.analysis_base_dir = analysis_base_dir
    
    def _get_output_dir(self, project: Project) -> Path:
        """
        Override to create output directory in analysis location.
        """
        # Create .output directory in analysis location, not production
        analysis_output_dir = project.project_path / ".output"
        analysis_output_dir.mkdir(parents=True, exist_ok=True)
        return analysis_output_dir
    
    def _copy_document(self, document, segment, destination_dir):
        """
        Override to skip actual file copying in analysis mode.
        """
        if self.logger:
            self.logger.distribution_info(f"[ANALYSIS MODE] Would copy {document.doc_id} to {destination_dir.name}")
        return True  # Simulate successful copy
    
    def _copy_to_output(self, source_path, destination_dir, doc_id):
        """
        Override to skip actual file copying in analysis mode.
        """
        if self.logger:
            self.logger.distribution_info(f"[ANALYSIS MODE] Would copy {doc_id} from {source_path} to {destination_dir}")
        return True  # Simulate successful copy

class AnalysisReferenceService(ReferenceSheetService):
    """
    Analysis-only reference service that skips PDF processing.
    """
    
    def __init__(self, film_number_service, analysis_base_dir: Path, logger=None):
        super().__init__(film_number_service, logger)
        self.analysis_base_dir = analysis_base_dir
    
    def generate_reference_sheets(self, project, active_roll=None):
        """
        Override to simulate reference sheet generation in analysis mode.
        Returns mock reference sheet data structure without creating actual files.
        """
        if not project.has_oversized:
            if self.logger:
                self.logger.reference_info("[ANALYSIS MODE] No oversized documents found, skipping reference sheet generation")
            return {}
        
        if self.logger:
            self.logger.reference_info(f"[ANALYSIS MODE] Simulating reference sheet generation for {project.documents_with_oversized} documents")
        
        # Simulate reference sheet data structure
        reference_sheets = {}
        
        # Process each document with oversized pages
        for document in project.documents:
            if not document.has_oversized or not document.ranges:
                continue
            
            doc_id = document.doc_id
            reference_sheets[doc_id] = []
            
            # Simulate reference sheet data for each oversized range
            for i, (range_start, range_end) in enumerate(document.ranges):
                # Create mock reference sheet entry
                mock_ref_path = f"[ANALYSIS_MODE]/{doc_id}_ref_{range_start}-{range_end}.pdf"
                reference_sheets[doc_id].append({
                    'path': mock_ref_path,
                    'range': (range_start, range_end),
                    'blip_35mm': f"[MOCK_BLIP_{i}]",
                    'film_number_35mm': f"[MOCK_FILM_{i}]"
                })
                
                if self.logger:
                    self.logger.reference_info(f"[ANALYSIS MODE] Simulated reference sheet for {doc_id}, range {range_start}-{range_end}")
        
        # Store reference sheet data in project
        project.reference_sheets = reference_sheets
        
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        if self.logger:
            self.logger.reference_success(f"[ANALYSIS MODE] Simulated {total_sheets} reference sheets for {len(reference_sheets)} documents")
        
        return reference_sheets
    
    def insert_reference_sheets(self, project, document, reference_sheets_data, output_dir=None):
        """
        Override to skip actual PDF processing in analysis mode.
        """
        if self.logger:
            self.logger.reference_info(f"[ANALYSIS MODE] Would insert reference sheets into {document.doc_id}")
        # Return a fake path to simulate processing
        return project.project_path / ".temp" / "processed" / f"{document.doc_id}.pdf"
    
    def insert_reference_sheets_for_35mm(self, project, document, reference_sheets_data, oversized_path):
        """
        Override to skip actual PDF processing for 35mm in analysis mode.
        """
        if self.logger:
            self.logger.reference_info(f"[ANALYSIS MODE] Would insert reference sheets for 35mm for document {document.doc_id}")
        # Return a fake path to simulate processing
        return project.project_path / ".temp" / "processed35" / f"{document.doc_id}_with_refs.pdf"
    
    def extract_all_oversized_pages(self, project, document, output_dir=None):
        """
        Override to skip actual PDF extraction in analysis mode.
        """
        if self.logger:
            self.logger.reference_info(f"[ANALYSIS MODE] Would extract oversized pages from document {document.doc_id}")
        # Return a fake path to simulate the extracted oversized document
        return project.project_path / ".temp" / "oversized35" / f"{document.doc_id}_oversized.pdf"

def scan_production_folders(production_drive: str = "X:/") -> List[Path]:
    """
    Scan production drive for project folders, excluding system folders.
    """
    production_path = Path(production_drive)
    project_folders = []
    
    # Folders to exclude
    exclude_folders = {
        "$RECYCLE.BIN", 
        "System Volume Information", 
        ".management",
        "archive.ico",
        "autorun.inf"
    }
    
    try:
        for item in production_path.iterdir():
            if item.is_dir() and item.name not in exclude_folders:
                # Check if it looks like a project folder (starts with RRD)
                if item.name.startswith("RRD"):
                    project_folders.append(item)
    except Exception as e:
        print(f"Error scanning production drive: {e}")
    
    return sorted(project_folders)

def analyze_single_project(production_project_path: Path, analysis_base_dir: Path, logger, project_progress_bar=None, drive_progress_bar=None) -> Dict[str, Any]:
    """
    Analyze a single project folder without modifying production data.
    """
    project_name = production_project_path.name
    
    # Estimate substeps for granular progress
    def estimate_project_steps(project_path):
        """Estimate total substeps based on project contents"""
        try:
            # Quick estimate: count PDF files to estimate document processing steps
            pdf_count = 0
            for item in project_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        # Look for PDF files in subdirectories (recursive)
                        for pdf_file in item.glob("**/*.pdf"):
                            pdf_count += 1
                    except:
                        continue
            
            # Base processing steps
            base_steps = 15  # init, allocation, indexing, export, etc.
            # Document processing: 1 step per document
            doc_steps = pdf_count
            
            total_steps = base_steps + doc_steps
            return total_steps
        except:
            return 50  # Higher default fallback
    
    total_steps = estimate_project_steps(production_project_path)
    current_step = 0
    
    def update_progress(description: str, steps: int = 1):
        nonlocal current_step
        current_step += steps
        
        if project_progress_bar:
            # Update project progress bar immediately
            project_progress_bar.set_description(f"{project_name[:20]}")
            if project_progress_bar.total != total_steps:
                project_progress_bar.total = total_steps
                project_progress_bar.refresh()
            project_progress_bar.update(steps)
            project_progress_bar.refresh()  # Force immediate update
        
        if drive_progress_bar:
            # Update drive progress bar immediately
            drive_progress_bar.update(steps)
            drive_progress_bar.refresh()  # Force immediate update
    
    try:
        # Stage 1: Initialize services
        update_progress("Initializing services", 1)
        analysis_project_service = AnalysisProjectService(analysis_base_dir, logger=logger)
        update_progress("Creating document service", 1)
        doc_service = DocumentProcessingService(logger=logger)
        analysis_film_number_service = AnalysisFilmNumberService(analysis_base_dir, logger=logger)
        analysis_reference_service = AnalysisReferenceService(
            analysis_film_number_service, analysis_base_dir, logger=logger
        )
        analysis_distribution_service = AnalysisDistributionService(
            analysis_base_dir,
            logger=logger,
            film_number_service=analysis_film_number_service,
            reference_service=analysis_reference_service
        )
        film_service = FilmService(logger=logger)
        index_service = IndexService(logger=logger)
        export_service = ExportService(logger=logger)
        update_progress("Services initialized", 1)
        
        # Initialize project for analysis
        update_progress("Loading project", 1)
        project = analysis_project_service.initialize_project_for_analysis(production_project_path)
        
        # Stage 2: Process documents with granular progress
        update_progress(f"Starting document processing", 1)
        
        # CRITICAL: Hook into the actual document processing loop
        # Monkey patch the _process_document method to add progress updates
        original_process_doc = doc_service._process_document
        original_process = doc_service.process_documents
        
        def process_document_with_progress(folder_path, document_file):
            # Update progress for this specific document
            doc_name = document_file.replace('.pdf', '')
            update_progress(f"Processing {doc_name}", 1)
            
            # Call the original processing method
            return original_process_doc(folder_path, document_file)
        
        # Replace the internal method that processes each document
        doc_service._process_document = process_document_with_progress
        
        # Actually process all documents (now with real progress updates)
        project = doc_service.process_documents(project)
        
        # Restore original methods
        doc_service._process_document = original_process_doc
        
        update_progress("Document processing complete", 1)
        
        # Branch workflow based on whether the project has oversized pages
        if project.has_oversized:            
            # Stage 3: Calculate reference pages (only for oversized projects)
            update_progress("Calculating reference pages", 1)
            update_progress("Processing oversized documents", 1)
            project = doc_service.calculate_references(project)
            update_progress("Reference calculation complete", 1)
            
            # Stage 4: Allocate documents to film rolls
            update_progress("Starting film allocation", 1)
            update_progress("Calculating 16mm requirements", 1)
            update_progress("Calculating 35mm requirements", 1)
            project = film_service.allocate_film(project)
            update_progress("Film allocation complete", 1)
            
            # Stage 5: Initialize index data
            update_progress("Building index structure", 1)
            update_progress("Processing document metadata", 1)
            index_data = index_service.initialize_index(project)
            update_progress("Index data complete", 1)
            
            # Stage 6: Allocate film numbers
            update_progress("Assigning film numbers", 1)
            update_progress("Database operations", 1)
            project, index_data = analysis_film_number_service.allocate_film_numbers(project, index_data)
            update_progress("Film numbers assigned", 1)
            
            # Stage 7: Simulate document distribution
            update_progress("Starting distribution simulation", 1)
            update_progress("Processing references", 1)
            project = analysis_distribution_service.distribute_documents(
                project, 
                film_number_service=analysis_film_number_service, 
                reference_service=analysis_reference_service
            )
            update_progress("Distribution complete", 1)
        else:            
            # Stage 3: Allocate documents to film rolls
            update_progress("Starting film allocation", 1)
            update_progress("Calculating requirements", 1)
            project = film_service.allocate_film(project)
            update_progress("Film allocation complete", 1)
            
            # Stage 4: Initialize index data
            update_progress("Building index structure", 1)
            update_progress("Processing metadata", 1)
            index_data = index_service.initialize_index(project)
            update_progress("Index data complete", 1)
            
            # Stage 5: Allocate film numbers
            update_progress("Assigning film numbers", 1)
            update_progress("Database operations", 1)
            project, index_data = analysis_film_number_service.allocate_film_numbers(project, index_data)
            update_progress("Film numbers assigned", 1)
            
            # Stage 6: Simulate document distribution
            update_progress("Starting distribution", 1)
            project = analysis_distribution_service.distribute_documents(
                project, 
                film_number_service=analysis_film_number_service, 
                reference_service=analysis_reference_service
            )
            update_progress("Distribution complete", 1)
        
        # Final stage: Export results
        update_progress("Preparing exports", 1)
        export_results = export_service.export_results(project, index_data)
        update_progress("Export complete", 1)
        
        # Clean up any .output directory that might have been created
        output_dir = project.project_path / ".output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
            logger.main_info(f"Cleaned up temporary .output directory")
        
        # Return analysis summary
        analysis_summary = {
            "project_name": project.project_folder_name,
            "archive_id": project.archive_id,
            "location": project.location,
            "doc_type": project.doc_type,
            "total_documents": len(project.documents),
            "total_pages": project.total_pages,
            "has_oversized": project.has_oversized,
            "total_oversized": project.total_oversized,
            "documents_with_oversized": project.documents_with_oversized,
            "total_pages_with_refs": project.total_pages_with_refs,
            "film_allocation": {
                "total_rolls_16mm": project.film_allocation.total_rolls_16mm if project.film_allocation else 0,
                "total_pages_16mm": project.film_allocation.total_pages_16mm if project.film_allocation else 0,
                "total_rolls_35mm": project.film_allocation.total_rolls_35mm if project.film_allocation else 0,
                "total_pages_35mm": project.film_allocation.total_pages_35mm if project.film_allocation else 0,
            },
            "export_paths": {name: str(path) for name, path in export_results.items()},
            "analysis_status": "completed"
        }
        
        logger.main_success(f"Analysis completed for {project.project_folder_name}")
        return analysis_summary
        
    except Exception as e:
        logger.main_error(f"Analysis failed for {production_project_path.name}: {str(e)}")
        return {
            "project_name": production_project_path.name,
            "analysis_status": "failed",
            "error": str(e)
        }

def main():
    """
    Main entry point for batch analysis of production folders.
    """
    parser = argparse.ArgumentParser(description="Microfilm Project Analysis System")
    parser.add_argument(
        "--production-drive",
        default="X:/",
        help="Production drive path (default: X:/)"
    )
    parser.add_argument(
        "--analysis-dir",
        default=r"C:\Users\user1\Desktop\microexcel\AnalysisResults",
        help="Analysis results directory"
    )
    parser.add_argument(
        "--logs-dir",
        default=r"C:\Users\user1\Desktop\microexcel\AnalysisResults\Logs",
        help="Logs directory"
    )
    parser.add_argument(
        "--single-project",
        help="Analyze only a specific project folder name"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Silent mode - only show progress bars, no other output"
    )
    args = parser.parse_args()
    
    # Set up paths
    analysis_base_dir = Path(args.analysis_dir)
    logs_dir = Path(args.logs_dir)
    
    # Create directories
    analysis_base_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger with silent mode support
    log_level = LogLevel.CRITICAL.value if args.silent else LogLevel.INFO.value
    logger = FilmLogger("Analysis", log_level=log_level, silent=args.silent)
    logger.parent_folder = str(logs_dir)
    logger.save_log_file(archive_id="BATCH_ANALYSIS")
    
    if not args.silent:
        # Initial setup messages (before progress bars)
        print("🚀 Starting batch analysis of production folders")
        print(f"📂 Production drive: {args.production_drive}")
        print(f"📁 Analysis output: {analysis_base_dir}")
        print(f"📄 Logs directory: {logs_dir}")
        print()
        
        # Scan for project folders
        print("🔍 Scanning production drive for project folders...")
    
    project_folders = scan_production_folders(args.production_drive)
    
    if not args.silent:
        print(f"✅ Found {len(project_folders)} project folders")
        print()
    
    # Filter for single project if specified
    if args.single_project:
        project_folders = [f for f in project_folders if f.name == args.single_project]
        if not project_folders:
            logger.main_error(f"Project folder '{args.single_project}' not found")
            return 1
        logger.main_info(f"Analyzing single project: {args.single_project}")
    
    # Process each project with progress bars
    analysis_results = []
    successful_analyses = 0
    failed_analyses = 0
    
    # Estimate total steps across all projects for granular drive progress
    def estimate_total_steps(folders):
        total = 0
        for folder in folders:
            try:
                # Quick estimate based on folder contents
                pdf_count = 0
                for item in folder.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        try:
                            # Look for PDF files in subdirectories
                            for pdf_file in item.glob("**/*.pdf"):
                                pdf_count += 1
                        except:
                            continue
                
                # Estimate steps per project based on actual PDF count
                base_steps = 15  # Base processing steps (init, allocation, etc.)
                doc_steps = pdf_count  # One step per document
                total += base_steps + doc_steps
                
                if not args.silent:
                    tqdm.write(f"Estimated {pdf_count} documents in {folder.name} = {base_steps + doc_steps} steps")
            except Exception as e:
                total += 50  # Higher default estimate per project
                if not args.silent:
                    tqdm.write(f"Could not estimate {folder.name}, using default 50 steps: {e}")
        
        if not args.silent:
            tqdm.write(f"Total estimated steps across all projects: {total}")
        return total
    
    total_drive_steps = estimate_total_steps(project_folders)
    
    # X drive level progress bar (overall progress across all projects)
    drive_progress = tqdm(
        total=total_drive_steps,
        desc="Drive",
        unit="step",
        position=0,
        leave=True,
        bar_format="{desc}: {percentage:5.2f}%|{bar}| {n_fmt}/{total_fmt} ({rate_fmt})",
        ncols=0,
        dynamic_ncols=True,
        colour="blue",
        mininterval=0,
        maxinterval=0.1,
        smoothing=0,
        file=sys.stdout
    )
    
    # Project level progress bar (substeps within current project)
    project_progress = tqdm(
        total=20,  # Will be adjusted per project based on estimated steps
        desc="Project",
        unit="step",
        position=1,
        leave=True,  # Make persistent
        bar_format="{desc}: {percentage:5.2f}%|{bar}| {n_fmt}/{total_fmt}",
        ncols=0,
        dynamic_ncols=True,
        colour="green",
        mininterval=0,
        maxinterval=0.1,
        smoothing=0,
        file=sys.stdout
    )
    
    # Set up logger wrapper to use tqdm.write
    logger_wrapper = TqdmLoggerWrapper(logger)
    
    try:
        for i, project_folder in enumerate(project_folders):
            # Reset project progress bar for new project (will be adjusted in analyze_single_project)
            project_progress.reset(total=20)
            project_progress.set_description(f"{project_folder.name[:20]}")
            
            # Update X drive progress description
            drive_progress.set_description(f"Drive ({successful_analyses}✅ {failed_analyses}❌)")
            
            # Use tqdm.write for logging so it doesn't interfere with progress bars
            if not args.silent:
                tqdm.write(f"\n📁 Processing {project_folder.name} ({i + 1}/{len(project_folders)})")
            
            try:
                result = analyze_single_project(project_folder, analysis_base_dir, logger, project_progress, drive_progress)
                analysis_results.append(result)
                
                if result.get("analysis_status") == "completed":
                    successful_analyses += 1
                    # Make sure progress bar shows completion
                    if project_progress.n < project_progress.total:
                        project_progress.update(project_progress.total - project_progress.n)
                    project_progress.set_description(f"✅ {project_folder.name[:15]}")
                    if not args.silent:
                        tqdm.write(f"✅ Successfully analyzed: {project_folder.name}")
                else:
                    failed_analyses += 1
                    project_progress.set_description(f"❌ {project_folder.name[:15]}")
                    if not args.silent:
                        tqdm.write(f"❌ Failed to analyze: {project_folder.name}")
                    
            except Exception as e:
                failed_analyses += 1
                error_msg = str(e)[:50]
                project_progress.set_description(f"💥 Error: {project_folder.name[:30]} - {error_msg[:20]}")
                if not args.silent:
                    tqdm.write(f"💥 Unexpected error processing {project_folder.name}: {str(e)}")
                analysis_results.append({
                    "project_name": project_folder.name,
                    "analysis_status": "failed",
                    "error": str(e)
                })
            
            # Drive progress is now updated within analyze_single_project
            
            # Small pause to see the completion status
            import time
            time.sleep(0.5)
    
    finally:
        # Restore original logger behavior
        logger_wrapper.restore()
        
        # Clean up progress bars
        project_progress.close()
        drive_progress.close()
    
    # Save batch analysis summary
    summary_path = analysis_base_dir / "batch_analysis_summary.json"
    batch_summary = {
        "analysis_date": datetime.now().isoformat(),
        "production_drive": args.production_drive,
        "total_projects": len(project_folders),
        "successful_analyses": successful_analyses,
        "failed_analyses": failed_analyses,
        "results": analysis_results
    }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(batch_summary, f, indent=2, ensure_ascii=False)
    
    # Final summary (after progress bars are closed)
    if not args.silent:
        print("\n" + "="*80)
        print("🎉 BATCH ANALYSIS COMPLETED!")
        print(f"✅ Successfully analyzed: {successful_analyses} projects")
        if failed_analyses > 0:
            print(f"❌ Failed analyses: {failed_analyses} projects")
        print(f"📊 Summary saved to: {summary_path}")
        print("="*80)
    
    return 0 if failed_analyses == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
