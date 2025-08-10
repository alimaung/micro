"""
Export Views Module

This module provides API views for export-related functionality,
including saving localStorage data to the filesystem and generating
export files.
"""

import json
import logging
import os
from pathlib import Path

from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.encoding import force_str

from microapp.models import Project
from microapp.services.export_manager import ExportManager

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def export_project_data(request, project_id):
    """
    API endpoint to export project data from localStorage.
    
    Accepts localStorage data from the frontend and saves it to the 
    appropriate project directory.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        
    Returns:
        JsonResponse with the result of the export operation
    """
    try:
        # Parse JSON data from request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data"
            }, status=400)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # Create export manager and export data
        export_manager = ExportManager()
        result = export_manager.export_project_data(project_id, data)
        
        # Return result
        if result["status"] == "success":
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=500)
    
    except Exception as e:
        logger.error(f"Error exporting project data: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to export project data: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def generate_exports(request, project_id):
    """
    API endpoint to generate additional export files for a project.
    
    Uses localStorage data previously saved to generate exports
    like CSV files, summary reports, etc.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        
    Returns:
        JsonResponse with the result of the export operation
    """
    try:
        # Get export directory from query parameters
        export_dir = request.GET.get('export_dir', None)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # Check if we have export directory
        if not export_dir:
            # Try to find the export directory in the default location
            export_manager = ExportManager()
            export_dir = None  # Let ExportManager find it
        
        # If export_dir is still None, ExportManager will try to find it
        export_manager = ExportManager()
        zip_path, _ = export_manager.create_export_zip(project_id, export_dir)
        
        if zip_path:
            return JsonResponse({
                "status": "success",
                "message": "Exports generated successfully",
                "zip_path": zip_path,
                "download_url": f"/api/export/{project_id}/download/?path={zip_path}"
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Failed to generate exports"
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error generating exports: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to generate exports: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def download_export_zip(request, project_id):
    """
    API endpoint to download a ZIP file containing all exports for a project.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        
    Returns:
        FileResponse with the ZIP file
    """
    try:
        # Get ZIP path from query parameters
        zip_path = request.GET.get('path', None)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # Check if we have a ZIP path
        if not zip_path:
            # Try to create a new ZIP
            export_manager = ExportManager()
            zip_path, memory_file = export_manager.create_export_zip(project_id)
            
            if not zip_path:
                return JsonResponse({
                    "status": "error",
                    "message": "Failed to create export ZIP"
                }, status=500)
        else:
            # Check if the ZIP file exists
            if not os.path.exists(zip_path):
                return JsonResponse({
                    "status": "error",
                    "message": "Export ZIP file not found"
                }, status=404)
        
        # Return the ZIP file
        archive_id = project.archive_id or f"project_{project.id}"
        filename = f"{archive_id}_exports.zip"
        
        response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        logger.error(f"Error downloading export ZIP: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to download export ZIP: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def download_specific_export(request, project_id, export_type):
    """
    API endpoint to download a specific export file for a project.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        export_type: Type of export to download (e.g., 'index', 'summary')
        
    Returns:
        FileResponse with the requested file
    """
    try:
        # Get export directory from query parameters
        export_dir = request.GET.get('dir', None)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # Map export_type to file pattern
        archive_id = project.archive_id or f"project_{project.id}"
        file_patterns = {
            'index': f"{archive_id}_index.csv",
            'summary': f"{archive_id}_summary.json",
            'project': "microfilmProjectState.json",
            'allocation': "microfilmAllocationData.json",
            'filmnumber': "microfilmFilmNumberResults.json",
            'distribution': "microfilmDistributionResults.json"
        }
        
        if export_type not in file_patterns:
            return JsonResponse({
                "status": "error",
                "message": f"Unknown export type: {export_type}"
            }, status=400)
        
        file_pattern = file_patterns[export_type]
        
        # Find the file
        if export_dir:
            export_dir_path = Path(export_dir)
            file_path = export_dir_path / file_pattern
        else:
            # Try to find in default location
            export_manager = ExportManager()
            dummy_data = {'microfilmProjectState': {'projectInfo': {'archiveId': archive_id}}}
            export_dir_path = export_manager._get_export_directory(project, dummy_data)
            
            # Look for files matching the pattern
            matching_files = list(export_dir_path.glob(file_pattern))
            if not matching_files:
                return JsonResponse({
                    "status": "error",
                    "message": f"Export file not found: {file_pattern}"
                }, status=404)
            
            file_path = matching_files[0]
        
        # Check if the file exists
        if not file_path.exists():
            return JsonResponse({
                "status": "error",
                "message": f"Export file not found: {file_path}"
            }, status=404)
        
        # Determine content type
        content_type = 'application/json'
        if file_pattern.endswith('.csv'):
            content_type = 'text/csv'
        elif file_pattern.endswith('.pdf'):
            content_type = 'application/pdf'
        
        # Return the file
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
        return response
    
    except Exception as e:
        logger.error(f"Error downloading specific export: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to download export: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def get_available_exports(request, project_id):
    """
    API endpoint to get a list of available exports for a project.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        
    Returns:
        JsonResponse with a list of available exports
    """
    try:
        # Get export directory from query parameters
        export_dir = request.GET.get('dir', None)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # If no export directory provided, try to find one
        if not export_dir:
            # Try to find in default locations
            export_manager = ExportManager()
            archive_id = project.archive_id or f"project_{project.id}"
            dummy_data = {'microfilmProjectState': {'projectInfo': {'archiveId': archive_id}}}
            export_dir_path = export_manager._get_export_directory(project, dummy_data)
        else:
            export_dir_path = Path(export_dir)
        
        # Check if the directory exists
        if not export_dir_path.exists() or not export_dir_path.is_dir():
            return JsonResponse({
                "status": "error",
                "message": f"Export directory not found: {export_dir_path}"
            }, status=404)
        
        # Get all files in the directory
        files = []
        for file_path in export_dir_path.glob('*'):
            if file_path.is_file():
                # Add file info
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "type": "application/json"  # Default content type
                }
                
                # Set content type based on extension
                if file_path.suffix == '.csv':
                    file_info["type"] = "text/csv"
                elif file_path.suffix == '.pdf':
                    file_info["type"] = "application/pdf"
                elif file_path.suffix == '.zip':
                    file_info["type"] = "application/zip"
                
                files.append(file_info)
        
        # Return list of files
        return JsonResponse({
            "status": "success",
            "export_dir": str(export_dir_path),
            "files": files
        })
    
    except Exception as e:
        logger.error(f"Error getting available exports: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to get available exports: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def reveal_in_explorer(request, project_id):
    """
    API endpoint to open a directory in the system's file explorer.
    
    Args:
        request: HTTP request object
        project_id: ID of the project
        
    Returns:
        JsonResponse with the result of the operation
    """
    try:
        # Get path from query parameters
        path = request.GET.get('path', None)
        
        # Validate the project exists
        project = get_object_or_404(Project, id=project_id)
        
        # Check if we have a path
        if not path:
            return JsonResponse({
                "status": "error",
                "message": "No path provided"
            }, status=400)
        
        # Check if the path exists
        path_obj = Path(path)
        if not path_obj.exists():
            return JsonResponse({
                "status": "error",
                "message": f"Path not found: {path}"
            }, status=404)
        
        # Open directory in file explorer - platform specific
        import platform
        import subprocess
        
        try:
            system = platform.system()
            if system == 'Windows':
                # For Windows
                os.startfile(path)
            elif system == 'Darwin':
                # For macOS
                subprocess.call(['open', path])
            else:
                # For Linux
                subprocess.call(['xdg-open', path])
                
            return JsonResponse({
                "status": "success",
                "message": f"Directory opened: {path}"
            })
        except Exception as e:
            logger.error(f"Error opening directory: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Failed to open directory: {str(e)}"
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error in reveal_in_explorer: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to reveal in explorer: {str(e)}"
        }, status=500)

@require_http_methods(["POST"])  # Upsert a single key of registration state
def save_register_state_key(request, project_id, key):
    """
    Save a single registration state key payload to a stable per-project state folder.

    Writes to: MEDIA_ROOT/register_state/<project_id>/<key>.json
    The request body should be a JSON object representing the value to store.
    Optionally supports a top-level {"data": <payload>} wrapper; if present, uses that.
    """
    try:
        project = get_object_or_404(Project, id=project_id)

        try:
            body = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)

        # Accept either raw JSON payload or {"data": payload}
        payload = body.get("data") if isinstance(body, dict) and "data" in body else body

        # Ensure state directory exists
        state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project_id)
        state_dir.mkdir(parents=True, exist_ok=True)
        file_path = state_dir / f"{key}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

        return JsonResponse({
            "status": "success",
            "message": "State saved",
            "path": str(file_path),
        })
    except Exception as e:
        logger.error(f"Error saving register state key {key} for project {project_id}: {str(e)}")
        return JsonResponse({"status": "error", "message": force_str(e)}, status=500)


@require_http_methods(["GET"])  # Read a single key of registration state
def get_register_state_key(request, project_id, key):
    """
    Get a stored registration state key payload.
    Looks in: MEDIA_ROOT/register_state/<project_id>/<key>.json
    """
    try:
        project = get_object_or_404(Project, id=project_id)
        state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project_id)
        file_path = state_dir / f"{key}.json"

        if not file_path.exists():
            return JsonResponse({"status": "error", "message": "Not found"}, status=404)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return JsonResponse({
            "status": "success",
            "data": data,
        })
    except Exception as e:
        logger.error(f"Error reading register state key {key} for project {project_id}: {str(e)}")
        return JsonResponse({"status": "error", "message": force_str(e)}, status=500)


@require_http_methods(["DELETE"])  # Delete a single key of registration state
def delete_register_state_key(request, project_id, key):
    """
    Delete a stored registration state key payload if present.
    """
    try:
        project = get_object_or_404(Project, id=project_id)
        state_dir = Path(settings.MEDIA_ROOT) / 'register_state' / str(project_id)
        file_path = state_dir / f"{key}.json"

        if file_path.exists():
            file_path.unlink()

        return JsonResponse({"status": "success", "message": "State deleted"})
    except Exception as e:
        logger.error(f"Error deleting register state key {key} for project {project_id}: {str(e)}")
        return JsonResponse({"status": "error", "message": force_str(e)}, status=500)
