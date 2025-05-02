"""
Project management views for the microapp.
These views handle CRUD operations for projects.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

from ..models import Project

@csrf_exempt
@login_required
def create_project(request):
    """
    API endpoint to create a new project.
    
    Args:
        Various project attributes in JSON request body
        
    Returns:
        JSON response with project ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create a new project with the basic information from transfer
            project = Project(
                archive_id=data.get('archive_id'),
                location=data.get('location'),
                doc_type=data.get('doc_type', ''),
                project_path=data.get('project_path'),
                project_folder_name=data.get('project_folder_name'),
                comlist_path=data.get('comlist_path'),
                output_dir=data.get('output_dir', ''),
                retain_sources=data.get('retain_sources', True),
                add_to_database=data.get('add_to_database', True),
                pdf_folder_path=data.get('pdf_folder_path', ''),
                has_pdf_folder=data.get('has_pdf_folder', False),
                owner=request.user
            )
            project.save()
            
            return JsonResponse({
                'status': 'success',
                'project_id': project.id,
                'message': f'Project {project.archive_id} created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def list_projects(request):
    """
    API endpoint to list all projects with filtering options.
    
    Args:
        Various filter parameters as GET parameters
        
    Returns:
        JSON response with paginated project list
    """
    try:
        # Get query parameters for filtering
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Initialize queryset with user's projects
        queryset = Project.objects.filter(owner=request.user)
        
        # Apply filters if provided
        archive_id = request.GET.get('archive_id')
        if archive_id:
            queryset = queryset.filter(archive_id__icontains=archive_id)
            
        location = request.GET.get('location')
        if location:
            queryset = queryset.filter(location__iexact=location)
            
        doc_type = request.GET.get('doc_type')
        if doc_type:
            queryset = queryset.filter(doc_type__iexact=doc_type)
            
        has_oversized = request.GET.get('has_oversized')
        if has_oversized is not None:
            has_oversized_bool = has_oversized.lower() in ['true', '1', 't', 'y', 'yes']
            queryset = queryset.filter(has_oversized=has_oversized_bool)
            
        # Date range filtering
        date_from = request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
            
        date_to = request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        # Search term
        search_term = request.GET.get('search')
        if search_term:
            queryset = queryset.filter(
                Q(archive_id__icontains=search_term) | 
                Q(project_folder_name__icontains=search_term) |
                Q(doc_type__icontains=search_term) |
                Q(location__icontains=search_term)
            )
            
        # Sorting
        sort_field = request.GET.get('sort_field', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # Map sort field to model field
        field_mapping = {
            'id': 'id',
            'created': 'created_at',
            'name': 'project_folder_name',
            'archive_id': 'archive_id',
            'location': 'location',
            'doc_type': 'doc_type',
            'total_pages': 'total_pages'
        }
        
        sort_field = field_mapping.get(sort_field, 'created_at')
        if sort_order.lower() == 'desc':
            sort_field = f'-{sort_field}'
            
        queryset = queryset.order_by(sort_field)
        
        # Count total records (for pagination)
        total_records = queryset.count()
        total_pages = (total_records + page_size - 1) // page_size  # Ceiling division
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_queryset = queryset[start:end]
        
        # Serialize paginated queryset
        projects_data = []
        for project in paginated_queryset:
            projects_data.append({
                'id': project.id,
                'project_id': project.id,  # For compatibility with the UI
                'archive_id': project.archive_id,
                'location': project.location,
                'doc_type': project.doc_type,
                'project_path': project.project_path,
                'project_folder_name': project.project_folder_name,
                'comlist_path': project.comlist_path,
                'output_dir': project.output_dir,
                'has_pdf_folder': project.has_pdf_folder,
                'processing_complete': project.processing_complete,
                'retain_sources': project.retain_sources,
                'add_to_database': project.add_to_database,
                'has_oversized': project.has_oversized,
                'total_pages': project.total_pages or 0,
                'total_pages_with_refs': project.total_pages_with_refs or 0,
                'date_created': project.created_at.strftime('%Y-%m-%d'),
                'updated_at': project.updated_at.strftime('%Y-%m-%d'),
                'owner': project.owner.username,
                # Additional fields for UI compatibility
                'folderName': project.project_folder_name,
                'path': project.project_path,
                'oversized': project.has_oversized,
                'data_dir': project.output_dir,
                'index_path': project.comlist_path
            })
        
        return JsonResponse({
            'status': 'success',
            'total': total_records,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': projects_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_project(request, project_id):
    """
    API endpoint to get a single project by ID.
    
    Args:
        project_id: Project ID (URL parameter)
        
    Returns:
        JSON response with project details
    """
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        
        project_data = {
            'id': project.id,
            'project_id': project.id,  # For compatibility with the UI
            'archive_id': project.archive_id,
            'location': project.location,
            'doc_type': project.doc_type,
            'project_path': project.project_path,
            'project_folder_name': project.project_folder_name,
            'comlist_path': project.comlist_path,
            'output_dir': project.output_dir,
            'has_pdf_folder': project.has_pdf_folder,
            'processing_complete': project.processing_complete,
            'retain_sources': project.retain_sources,
            'add_to_database': project.add_to_database,
            'has_oversized': project.has_oversized,
            'total_pages': project.total_pages or 0,
            'total_pages_with_refs': project.total_pages_with_refs or 0,
            'date_created': project.created_at.strftime('%Y-%m-%d'),
            'updated_at': project.updated_at.strftime('%Y-%m-%d'),
            'owner': project.owner.username,
            # Additional fields for UI compatibility
            'folderName': project.project_folder_name,
            'path': project.project_path,
            'oversized': project.has_oversized,
            'data_dir': project.output_dir,
            'index_path': project.comlist_path
        }
        
        return JsonResponse({
            'status': 'success',
            'project': project_data
        })
        
    except Project.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Project not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@login_required
def update_project(request, project_id):
    """
    API endpoint to update a project.
    
    Args:
        project_id: Project ID (URL parameter)
        Various project attributes in JSON request body
        
    Returns:
        JSON response with status and message
    """
    if request.method == 'PUT':
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
            data = json.loads(request.body)
            
            # Update project fields if provided in the request
            if 'archive_id' in data:
                project.archive_id = data['archive_id']
            if 'location' in data:
                project.location = data['location']
            if 'doc_type' in data:
                project.doc_type = data['doc_type']
            if 'project_path' in data:
                project.project_path = data['project_path']
            if 'project_folder_name' in data:
                project.project_folder_name = data['project_folder_name']
            if 'comlist_path' in data:
                project.comlist_path = data['comlist_path']
            if 'output_dir' in data:
                project.output_dir = data['output_dir']
            if 'has_pdf_folder' in data:
                project.has_pdf_folder = data['has_pdf_folder']
            if 'processing_complete' in data:
                project.processing_complete = data['processing_complete']
            if 'retain_sources' in data:
                project.retain_sources = data['retain_sources']
            if 'add_to_database' in data:
                project.add_to_database = data['add_to_database']
            if 'has_oversized' in data:
                project.has_oversized = data['has_oversized']
            if 'total_pages' in data:
                project.total_pages = data['total_pages']
            if 'total_pages_with_refs' in data:
                project.total_pages_with_refs = data['total_pages_with_refs']
            if 'pdf_folder_path' in data:
                project.pdf_folder_path = data['pdf_folder_path']
                
            # Save the updated project
            project.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Project {project.archive_id} updated successfully'
            })
            
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Project not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def delete_project(request, project_id):
    """
    API endpoint to delete a project.
    
    Args:
        project_id: Project ID (URL parameter)
        
    Returns:
        JSON response with status and message
    """
    if request.method == 'DELETE':
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
            archive_id = project.archive_id
            project.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Project {archive_id} deleted successfully'
            })
            
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Project not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def get_database_stats(request):
    """
    API endpoint to get database statistics.
    
    Returns:
        JSON response with database statistics
    """
    try:
        # Get counts for each entity
        total_projects = Project.objects.filter(owner=request.user).count()
        
        # For now, we only have Project model, but we can add more in the future
        total_rolls = 0  # Will be implemented when Roll model is created
        total_documents = 0  # Will be implemented when Document model is created
        
        return JsonResponse({
            'status': 'success',
            'stats': {
                'total_projects': total_projects,
                'total_rolls': total_rolls,
                'total_documents': total_documents
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400) 