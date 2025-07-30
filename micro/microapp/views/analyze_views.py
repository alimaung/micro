"""
Analyze Views - Handle analysis and visualization of project data
"""

import json
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import Project
from ..services.analyze_service import AnalyzeService

logger = logging.getLogger(__name__)

@login_required
def analyze_dashboard(request):
    """Main analyze dashboard showing three sections: unregistered, analyzed, and registered projects"""
    analyze_service = AnalyzeService()
    
    # Get the current section filter
    section_filter = request.GET.get('section', 'all')  # all, unregistered, analyzed, registered
    search_query = request.GET.get('search', '')
    
    # Initialize sections data
    sections_data = {
        'unregistered': [],
        'analyzed': [],
        'registered': []
    }
    
    # Section 1: Unregistered/Unanalyzed folders
    if section_filter in ['all', 'unregistered']:
        unregistered_folders = analyze_service.discover_unregistered_folders()
        
        # Apply search filter to unregistered folders
        if search_query:
            filtered_unregistered = []
            for folder in unregistered_folders:
                if (search_query.lower() in folder['folder_name'].lower() or
                    search_query.lower() in folder['folder_path'].lower()):
                    filtered_unregistered.append(folder)
            unregistered_folders = filtered_unregistered
        
        sections_data['unregistered'] = unregistered_folders
    
    # Section 2: Analyzed but not registered folders
    if section_filter in ['all', 'analyzed']:
        analyzed_folders = analyze_service.get_analyzed_folders()
        
        # Apply search filter to analyzed folders
        if search_query:
            analyzed_folders = analyzed_folders.filter(
                Q(folder_name__icontains=search_query) |
                Q(folder_path__icontains=search_query)
            )
        
        # Convert to list with analysis summary
        analyzed_list = []
        for folder in analyzed_folders:
            folder_data = folder.analysis_summary
            folder_data['id'] = folder.id
            folder_data['folder_name'] = folder.folder_name
            folder_data['folder_path'] = folder.folder_path
            folder_data['analyzed_at'] = folder.analyzed_at
            folder_data['analyzed_by'] = folder.analyzed_by
            analyzed_list.append(folder_data)
        
        sections_data['analyzed'] = analyzed_list
    
    # Section 3: Registered projects (no filtering by status - show all)
    if section_filter in ['all', 'registered']:
        projects_with_data = analyze_service.get_registered_projects_with_data()
        
        # Apply search filter to registered projects
        if search_query:
            filtered_projects = []
            for item in projects_with_data:
                project = item['project']
                if (search_query.lower() in project.archive_id.lower() or
                    search_query.lower() in (project.location or '').lower() or
                    search_query.lower() in (project.doc_type or '').lower() or
                    search_query.lower() in (project.name or '').lower()):
                    filtered_projects.append(item)
            projects_with_data = filtered_projects
        
        sections_data['registered'] = projects_with_data
    
    # Calculate summary statistics across all sections
    total_unregistered = len(sections_data['unregistered'])
    total_analyzed = len(sections_data['analyzed'])
    total_registered = len(sections_data['registered'])
    
    # Summary stats for analyzed folders
    analyzed_total_docs = sum(item.get('total_documents', 0) for item in sections_data['analyzed'])
    analyzed_total_pages = sum(item.get('total_pages', 0) for item in sections_data['analyzed'])
    analyzed_with_oversized = sum(1 for item in sections_data['analyzed'] if item.get('has_oversized', False))
    
    # Summary stats for registered projects
    registered_total_docs = sum(item['data'].get('total_documents', 0) for item in sections_data['registered'])
    registered_total_pages = sum(item['data'].get('total_pages', 0) for item in sections_data['registered'])
    registered_with_oversized = sum(1 for item in sections_data['registered'] if item['data'].get('has_oversized', False))
    
    # Pagination - apply to the current section or all data
    if section_filter == 'unregistered':
        paginate_data = sections_data['unregistered']
    elif section_filter == 'analyzed':
        paginate_data = sections_data['analyzed']
    elif section_filter == 'registered':
        paginate_data = sections_data['registered']
    else:
        # For 'all', combine all sections for pagination
        paginate_data = (
            [{'type': 'unregistered', 'data': item} for item in sections_data['unregistered']] +
            [{'type': 'analyzed', 'data': item} for item in sections_data['analyzed']] +
            [{'type': 'registered', 'data': item} for item in sections_data['registered']]
        )
    
    paginator = Paginator(paginate_data, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sections_data': sections_data,
        'search_query': search_query,
        'section_filter': section_filter,
        'summary_stats': {
            'total_unregistered': total_unregistered,
            'total_analyzed': total_analyzed,
            'total_registered': total_registered,
            'analyzed_total_documents': analyzed_total_docs,
            'analyzed_total_pages': analyzed_total_pages,
            'analyzed_with_oversized': analyzed_with_oversized,
            'registered_total_documents': registered_total_docs,
            'registered_total_pages': registered_total_pages,
            'registered_with_oversized': registered_with_oversized
        }
    }
    
    return render(request, 'microapp/analyze/analyze.html', context)

@login_required
def analyze_project_detail(request, project_id):
    """Detailed analysis view for a specific project"""
    project = get_object_or_404(Project, id=project_id)
    analyze_service = AnalyzeService()
    
    # Get full analysis data for the project
    analysis_data = analyze_service.get_project_analysis_data(project_id)
    
    # Process and structure the data for the template
    context = {
        'project': project,
        'analysis_data': analysis_data
    }
    
    # Extract and structure key information
    if analysis_data:
        # Project state information
        if 'projectstatedata' in analysis_data:
            project_state = analysis_data['projectstatedata']
            context['project_state'] = project_state
            context['source_data'] = project_state.get('sourceData', {})
            context['project_info'] = project_state.get('projectInfo', {})
        
        # Analysis results
        if 'analysisdata' in analysis_data:
            analysis_results = analysis_data['analysisdata'].get('analysisResults', {})
            context['analysis_results'] = analysis_results
            context['documents'] = analysis_results.get('documents', [])[:50]  # Limit to first 50 for display
            context['total_documents_count'] = len(analysis_results.get('documents', []))
        
        # Allocation results
        if 'allocationdata' in analysis_data:
            allocation_results = analysis_data['allocationdata'].get('allocationResults', {})
            context['allocation_results'] = allocation_results
            
            if 'results' in allocation_results:
                allocation_data = allocation_results['results']
                rolls_16mm = allocation_data.get('rolls_16mm', [])
                rolls_35mm = allocation_data.get('rolls_35mm', [])
                temp_rolls = allocation_data.get('temp_rolls', [])
                
                # Add percentage calculations for rolls
                for roll in rolls_16mm:
                    if roll.get('capacity', 0) > 0:
                        roll['usage_percentage'] = int((roll.get('pages_used', 0) / roll['capacity']) * 100)
                    else:
                        roll['usage_percentage'] = 0
                        
                for roll in rolls_35mm:
                    if roll.get('capacity', 0) > 0:
                        roll['usage_percentage'] = int((roll.get('pages_used', 0) / roll['capacity']) * 100)
                    else:
                        roll['usage_percentage'] = 0
                
                context['rolls_16mm'] = rolls_16mm
                context['rolls_35mm'] = rolls_35mm
                context['temp_rolls'] = temp_rolls
                context['total_film_rolls'] = len(rolls_16mm) + len(rolls_35mm)
        
        # Index data
        if 'indexdata' in analysis_data:
            context['index_data'] = analysis_data['indexdata']
        
        # Film number results
        if 'filmnumberresults' in analysis_data:
            context['film_number_results'] = analysis_data['filmnumberresults']
    
    return render(request, 'microapp/analyze/project_detail.html', context)

@login_required
def analyze_project_data_api(request, project_id):
    """API endpoint to get project analysis data as JSON"""
    project = get_object_or_404(Project, id=project_id)
    analyze_service = AnalyzeService()
    
    analysis_data = analyze_service.get_project_analysis_data(project_id)
    
    return JsonResponse({
        'project_id': project_id,
        'archive_id': project.archive_id,
        'analysis_data': analysis_data
    })

@login_required
def analyze_refresh_data(request, project_id):
    """Refresh cached analysis data for a project"""
    from django.core.cache import cache
    
    # Clear cache for this project's data files
    cache_keys = [
        f"analyze_data_microfilmProjectState.json",
        f"analyze_data_microfilmAnalysisData.json",
        f"analyze_data_microfilmAllocationData.json",
        f"analyze_data_microfilmIndexData.json",
        f"analyze_data_microfilmFilmNumberResults.json"
    ]
    
    for key in cache_keys:
        cache.delete(key)
    
    return JsonResponse({'status': 'success', 'message': 'Data cache cleared'})

@login_required
def analyze_export_data(request, project_id):
    """Export project analysis data as downloadable JSON"""
    project = get_object_or_404(Project, id=project_id)
    analyze_service = AnalyzeService()
    
    analysis_data = analyze_service.get_project_analysis_data(project_id)
    
    response = JsonResponse(analysis_data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{project.archive_id}_analysis_data.json"'
    
    return response

@login_required
def analyze_folder_api(request):
    """API endpoint to analyze a folder without registering it"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        folder_path = data.get('folder_path')
        force_reanalyze = data.get('force_reanalyze', False)
        
        if not folder_path:
            return JsonResponse({'error': 'folder_path is required'}, status=400)
        
        analyze_service = AnalyzeService()
        analyzed_folder = analyze_service.analyze_folder_standalone(
            folder_path, request.user, force_reanalyze
        )
        
        if analyzed_folder:
            return JsonResponse({
                'status': 'success',
                'message': 'Folder analyzed successfully',
                'data': {
                    'id': analyzed_folder.id,
                    'folder_name': analyzed_folder.folder_name,
                    'folder_path': analyzed_folder.folder_path,
                    **analyzed_folder.analysis_summary
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to analyze folder'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error analyzing folder: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error analyzing folder: {str(e)}'
        }, status=500)

@login_required
def register_analyzed_folder_api(request):
    """API endpoint to register an analyzed folder as a project"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        analyzed_folder_id = data.get('analyzed_folder_id')
        project_data = data.get('project_data', {})
        
        if not analyzed_folder_id:
            return JsonResponse({'error': 'analyzed_folder_id is required'}, status=400)
        
        # Validate required project data
        required_fields = ['archive_id', 'location']
        for field in required_fields:
            if not project_data.get(field):
                return JsonResponse({'error': f'{field} is required in project_data'}, status=400)
        
        analyze_service = AnalyzeService()
        project = analyze_service.register_analyzed_folder_as_project(
            analyzed_folder_id, project_data
        )
        
        if project:
            return JsonResponse({
                'status': 'success',
                'message': 'Folder registered as project successfully',
                'data': {
                    'project_id': project.id,
                    'archive_id': project.archive_id,
                    'name': project.name,
                    'location': project.location
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to register folder as project'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error registering analyzed folder: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error registering folder: {str(e)}'
        }, status=500)

@login_required
def get_folder_basic_info_api(request):
    """API endpoint to get basic folder information"""
    folder_path = request.GET.get('folder_path')
    
    if not folder_path:
        return JsonResponse({'error': 'folder_path parameter is required'}, status=400)
    
    try:
        analyze_service = AnalyzeService()
        folder_info = analyze_service._get_basic_folder_info(folder_path)
        
        if folder_info:
            return JsonResponse({
                'status': 'success',
                'data': folder_info
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Could not get folder information'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error getting folder info: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting folder info: {str(e)}'
        }, status=500) 