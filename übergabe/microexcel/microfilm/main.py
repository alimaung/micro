"""
Main module for the microfilm processing system.

This module serves as the entry point for the microfilm processing system
and demonstrates how to use the ProjectService to initialize and manage projects.
"""

import sys, os
import argparse
from pathlib import Path
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
import json

def parse_arguments(args=None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments to parse. If None, sys.argv is used.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Microfilm Processing System")
    
    # Add arguments
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to project folder or document subfolder"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information"
    )

    return parser.parse_args(args)


def main(path=None, debug=False) -> int:
    """
    Main entry point for the microfilm processing system.
    
    Can be called directly or through command line arguments.
    
    Args:
        path: Path to project folder or document subfolder. If None and called from
              command line, it will be taken from args or user input.
        debug: Whether to show debug information.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Initialize with default log directory first
    logger = FilmLogger("Main", log_level=LogLevel.DEBUG.value)
    
    logger.main_info("Starting microfilm processing system")

    # Parse arguments if called from command line
    if path is None and (sys.argv[0].endswith('main.py') or sys.argv[0].endswith('main')):
        args = parse_arguments()
        path = args.path
        debug = args.debug
    
    try:
        # Get input path if not provided
        if not path:
            path = input("Enter path to project or document folder: ")

        # Initialize services
        project_service = ProjectService(logger=logger)
        doc_service = DocumentProcessingService(logger=logger)
        film_number_service = FilmNumberService(logger=logger)
        reference_service = ReferenceSheetService(film_number_service, logger=logger)
        doc_distribution_service = DocumentDistributionService(
            logger=logger,
            film_number_service=film_number_service,
            reference_service=reference_service
        )
        film_service = FilmService(logger=logger)
        index_service = IndexService(logger=logger)
        export_service = ExportService(logger=logger)
        
        # Initialize project
        project = project_service.initialize_project(path)
        
        # Configure logger to save logs in the project directory
        project_service.configure_logger(project, logger)
            
        # Process documents to identify oversized pages
        project = doc_service.process_documents(project)
        
        # Branch workflow based on whether the project has oversized pages
        if project.has_oversized:
            logger.main_info("Project has oversized pages, following oversized workflow")
            
            # Calculate reference pages for oversized documents
            project = doc_service.calculate_references(project)
            
            # Allocate documents to film rolls (both 16mm and 35mm)
            project = film_service.allocate_film(project)
            
            # Initialize index data
            index_data = index_service.initialize_index(project)
            
            # Allocate film numbers and update index
            project, index_data = film_number_service.allocate_film_numbers(project, index_data)
            
            # Process and distribute documents with oversized pages
            logger.main_info("Starting document distribution for project with oversized pages")
            project = doc_distribution_service.distribute_documents(
                project, 
                film_number_service=film_number_service, 
                reference_service=reference_service
            )
        else:
            logger.main_info("Project has no oversized pages, following standard workflow")
            
            # Allocate documents to film rolls (16mm only)
            project = film_service.allocate_film(project)
            
            # Initialize index data
            index_data = index_service.initialize_index(project)
            
            # Allocate film numbers and update index
            project, index_data = film_number_service.allocate_film_numbers(project, index_data)
            
            # Distribute documents to roll directories (standard)
            logger.main_info("Starting document distribution for standard project")
            project = doc_distribution_service.distribute_documents(
                project, 
                film_number_service=film_number_service, 
                reference_service=reference_service,
            )
        
                
        # Report distribution results
        if hasattr(project, 'distribution_results'):
            results = project.distribution_results
            logger.main_success(f"Document distribution completed: {results.get('processed_count', 0)} documents processed")
            if results.get('error_count', 0) > 0:
                logger.main_warning(f"Encountered {results.get('error_count')} errors during distribution")
            if results.get('output_dir'):
                logger.main_info(f"Documents distributed to: {results.get('output_dir')}")
        
        # Export results
        export_results = export_service.export_results(project, index_data)
        print(f"Project Path: {project.project_path}")
        
        # Get the data directory path from one of the result paths
        if export_results:
            data_dir = next(iter(export_results.values())).parent
            logger.main_info(f"Exported results to {data_dir}")
            
            # Open the data directory in the file explorer
            #os.startfile(data_dir)
        else:
            logger.main_warning("No results were exported")
        
        # Display project information if requested
        if debug:
            logger.main_debug("Project Details:")
            logger.main_debug(f"Archive ID: {project.archive_id}")
            logger.main_debug(f"Location: {project.location} (code: {project.location_code})")
            logger.main_debug(f"Document Type: {project.doc_type}")
            logger.main_debug(f"Project Path: {project.project_path}")
            
            if project.has_document_folder:
                logger.main_debug(f"Document Folder: {project.document_folder_path}")
            else:
                logger.main_debug("Document Folder: Not found (using project folder)")
            
            logger.main_debug(f"Documents Path: {project.documents_path}")
            logger.main_debug(f"Output Directory: {project.output_dir}")
            
            if project.comlist_path:
                logger.main_debug(f"COM List File: {project.comlist_path}")
            else:
                logger.main_debug("COM List File: Not found")
                
            # Add new debug information about documents and oversized pages
            logger.main_debug(f"Has Oversized Pages: {project.has_oversized}")
            logger.main_debug(f"Total Documents: {len(project.documents)}")
            logger.main_debug(f"Total Pages: {project.total_pages}")
            logger.main_debug(f"Total Pages with References: {project.total_pages_with_refs}")
            logger.main_debug(f"Total Oversized Pages: {project.total_oversized}")
            logger.main_debug(f"Documents with Oversized Pages: {project.documents_with_oversized}")
            
            # Show details of oversized documents if any
            if project.has_oversized and project.documents_with_oversized > 0:
                logger.main_debug("Oversized Documents:")
                for doc in project.documents:
                    if doc.has_oversized:
                        logger.main_debug(f"  - {doc.doc_id}: {doc.total_oversized} oversized pages, {doc.total_references} reference sheets")
            
            # Show film allocation details if available
            if project.film_allocation:
                logger.main_debug("Film Allocation:")
                logger.main_debug(f"  16mm Rolls: {project.film_allocation.total_rolls_16mm}")
                logger.main_debug(f"  16mm Pages: {project.film_allocation.total_pages_16mm}")
                
                if project.has_oversized:
                    logger.main_debug(f"  35mm Rolls: {project.film_allocation.total_rolls_35mm}")
                    logger.main_debug(f"  35mm Pages: {project.film_allocation.total_pages_35mm}")
                
                # Show index information
                logger.main_debug(f"Index Entries: {len(index_data['index'])}")
            
            # Show export information
            logger.main_debug("Export Paths:")
            for name, path in export_results.items():
                logger.main_debug(f"  {name}: {path}")
            
            # Show distribution results if available
            if hasattr(project, 'distribution_results') and project.distribution_results:
                logger.main_debug("Distribution Results:")
                for key, value in project.distribution_results.items():
                    logger.main_debug(f"  {key}: {value}")
        
        logger.main_success("Project processed successfully")
        return 0
        
    except ValueError as e:
        logger.main_error(f"Error: {str(e)}")
        return 1
    except Exception as e:
        logger.main_critical(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 