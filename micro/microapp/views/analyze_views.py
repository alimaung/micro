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
    section_filter = request.GET.get('section', 'all')  # all, unanalyzed, analyzed, registered
    search_query = request.GET.get('search', '')
    
    # Get sorting parameters
    sort_field = request.GET.get('sort', 'name')  # name, size, pages, documents, date
    sort_direction = request.GET.get('dir', 'asc')  # asc, desc
    
    # Initialize sections data
    sections_data = {
        'unanalyzed': [],
        'analyzed': [],
        'registered': []
    }
    
    # Section 1: Unanalyzed folders (truly unknown folders that haven't been analyzed)
    if section_filter in ['all', 'unanalyzed']:
        print(f"\n=== VIEW DEBUG: Getting unanalyzed folders ===")
        # Get unanalyzed folders (discover_unregistered_folders already excludes analyzed ones)
        unanalyzed_folders = analyze_service.discover_unregistered_folders()
        print(f"Raw unanalyzed folders count: {len(unanalyzed_folders)}")
        for folder in unanalyzed_folders:
            print(f"  - Unanalyzed: {folder['folder_name']} at {folder['folder_path']}")
        
        # Apply search filter to unanalyzed folders
        if search_query:
            filtered_unanalyzed = []
            for folder in unanalyzed_folders:
                if (search_query.lower() in folder['folder_name'].lower() or
                    search_query.lower() in folder['folder_path'].lower()):
                    filtered_unanalyzed.append(folder)
            unanalyzed_folders = filtered_unanalyzed
            print(f"After search filter: {len(unanalyzed_folders)} folders")
        
        # Apply sorting to unanalyzed folders
        sections_data['unanalyzed'] = sort_folder_data(unanalyzed_folders, sort_field, sort_direction, 'unanalyzed')
        print(f"Final unanalyzed folders: {len(sections_data['unanalyzed'])}")
        print("=== END VIEW DEBUG ===\n")
    
    # Section 2: Analyzed but not registered folders
    if section_filter in ['all', 'analyzed']:
        print(f"\n=== VIEW DEBUG: Getting analyzed folders ===")
        analyzed_folders = analyze_service.get_analyzed_folders()
        print(f"Raw analyzed folders from DB: {analyzed_folders.count()}")
        for folder in analyzed_folders:
            print(f"  - Analyzed DB: {folder.folder_name} at {folder.folder_path}")
        
        # Filter out folders that have already been registered as projects
        # Use the registered_as_project field to exclude folders that have been registered
        unregistered_analyzed_folders = analyzed_folders.filter(registered_as_project__isnull=True)
        print(f"After excluding registered (using registered_as_project field): {unregistered_analyzed_folders.count()}")
        
        # Also debug: show which folders are registered
        registered_analyzed_folders = analyzed_folders.filter(registered_as_project__isnull=False)
        print(f"Registered analyzed folders (should be excluded): {registered_analyzed_folders.count()}")
        for folder in registered_analyzed_folders:
            print(f"  - Registered: {folder.folder_name} -> Project ID: {folder.registered_as_project.id if folder.registered_as_project else 'None'}")
        
        analyzed_folders = unregistered_analyzed_folders
        
        # Apply search filter to analyzed folders
        if search_query:
            analyzed_folders = analyzed_folders.filter(
                Q(folder_name__icontains=search_query) |
                Q(folder_path__icontains=search_query)
            )
            print(f"After search filter: {analyzed_folders.count()}")
        
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
            print(f"  - Final Analyzed: {folder.folder_name} at {folder.folder_path}")
        
        # Apply sorting to analyzed folders
        print(f"DEBUG: Before sorting analyzed folders - count: {len(analyzed_list)}, sort_field: {sort_field}, sort_direction: {sort_direction}")
        if analyzed_list:
            print(f"DEBUG: Sample analyzed folder data keys: {list(analyzed_list[0].keys())}")
            if sort_field == 'size':
                print(f"DEBUG: Sample total_size values: {[item.get('total_size', 'MISSING') for item in analyzed_list[:3]]}")
        sections_data['analyzed'] = sort_folder_data(analyzed_list, sort_field, sort_direction, 'analyzed')
        print(f"Final analyzed folders: {len(sections_data['analyzed'])}")
        print("=== END ANALYZED DEBUG ===\n")
    
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
        
        # Apply sorting to registered projects
        sections_data['registered'] = sort_folder_data(projects_with_data, sort_field, sort_direction, 'registered')
    
    # Calculate summary statistics across all sections
    total_unanalyzed = len(sections_data['unanalyzed'])
    total_analyzed = len(sections_data['analyzed'])
    total_registered = len(sections_data['registered'])
    
    # Enhanced stats for unanalyzed folders
    unanalyzed_total_files = sum(item.get('file_count', 0) for item in sections_data['unanalyzed'])
    unanalyzed_total_size = sum(item.get('total_size', 0) for item in sections_data['unanalyzed'])
    unanalyzed_total_pdfs = sum(item.get('pdf_count', 0) for item in sections_data['unanalyzed'])
    unanalyzed_total_excel = sum(item.get('excel_count', 0) for item in sections_data['unanalyzed'])
    unanalyzed_total_other = sum(item.get('other_count', 0) for item in sections_data['unanalyzed'])
    
    # Enhanced stats for analyzed folders
    analyzed_total_docs = sum(item.get('total_documents', 0) for item in sections_data['analyzed'])
    analyzed_total_pages = sum(item.get('total_pages', 0) for item in sections_data['analyzed'])
    analyzed_with_oversized = sum(1 for item in sections_data['analyzed'] if item.get('has_oversized', False))
    analyzed_total_oversized = sum(item.get('oversized_count', 0) for item in sections_data['analyzed'])
    analyzed_total_16mm = sum(item.get('estimated_rolls_16mm', 0) for item in sections_data['analyzed'])
    analyzed_total_35mm = sum(item.get('estimated_rolls_35mm', 0) for item in sections_data['analyzed'])
    analyzed_total_size = sum(item.get('total_size', 0) for item in sections_data['analyzed'] if item.get('total_size'))
    analyzed_temp_rolls_created = sum(item.get('estimated_temp_rolls_created', 0) for item in sections_data['analyzed'])
    analyzed_temp_rolls_used = sum(item.get('estimated_temp_rolls_used', 0) for item in sections_data['analyzed'])
    
    # Calculate average utilization for analyzed folders
    analyzed_utilization_values = [item.get('overall_utilization', 0) for item in sections_data['analyzed'] if item.get('overall_utilization', 0) > 0]
    analyzed_avg_utilization = sum(analyzed_utilization_values) / len(analyzed_utilization_values) if analyzed_utilization_values else 0
    
    # Enhanced stats for registered projects
    registered_total_docs = sum(item['data'].get('total_documents', 0) for item in sections_data['registered'])
    registered_total_pages = sum(item['data'].get('total_pages', 0) for item in sections_data['registered'])
    registered_with_oversized = sum(1 for item in sections_data['registered'] if item['data'].get('has_oversized', False))
    registered_total_rolls = sum(item['data'].get('total_rolls', 0) for item in sections_data['registered'])
    registered_total_size = sum(item['data'].get('total_size', 0) for item in sections_data['registered'] if item['data'].get('total_size'))
    registered_temp_rolls_created = sum(item['data'].get('temp_rolls_created', 0) for item in sections_data['registered'])
    registered_temp_rolls_used = sum(item['data'].get('temp_rolls_used', 0) for item in sections_data['registered'])
    
    # Pagination - apply to the current section or all data
    if section_filter == 'unanalyzed':
        paginate_data = sections_data['unanalyzed']
    elif section_filter == 'analyzed':
        paginate_data = sections_data['analyzed']
    elif section_filter == 'registered':
        paginate_data = sections_data['registered']
    else:
        # For 'all', combine all sections for pagination
        paginate_data = (
            [{'type': 'unanalyzed', 'data': item} for item in sections_data['unanalyzed']] +
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
        'sort_field': sort_field,
        'sort_direction': sort_direction,
        'summary_stats': {
            'total_unanalyzed': total_unanalyzed,
            'total_analyzed': total_analyzed,
            'total_registered': total_registered,
            # Unanalyzed stats
            'unanalyzed_total_files': unanalyzed_total_files,
            'unanalyzed_total_size': unanalyzed_total_size,
            'unanalyzed_total_size_formatted': analyze_service.format_file_size(unanalyzed_total_size),
            'unanalyzed_total_pdfs': unanalyzed_total_pdfs,
            'unanalyzed_total_excel': unanalyzed_total_excel,
            'unanalyzed_total_other': unanalyzed_total_other,
            # Analyzed stats
            'analyzed_total_documents': analyzed_total_docs,
            'analyzed_total_pages': analyzed_total_pages,
            'analyzed_with_oversized': analyzed_with_oversized,
            'analyzed_total_oversized': analyzed_total_oversized,
            'analyzed_total_16mm': analyzed_total_16mm,
            'analyzed_total_35mm': analyzed_total_35mm,
            'analyzed_total_size': analyzed_total_size,
            'analyzed_total_size_formatted': analyze_service.format_file_size(analyzed_total_size),
            'analyzed_avg_utilization': round(analyzed_avg_utilization, 1),
            'analyzed_temp_rolls_created': analyzed_temp_rolls_created,
            'analyzed_temp_rolls_used': analyzed_temp_rolls_used,
            # Registered stats
            'registered_total_documents': registered_total_docs,
            'registered_total_pages': registered_total_pages,
            'registered_with_oversized': registered_with_oversized,
            'registered_total_rolls': registered_total_rolls,
            'registered_total_size': registered_total_size,
            'registered_total_size_formatted': analyze_service.format_file_size(registered_total_size),
            'registered_temp_rolls_created': registered_temp_rolls_created,
            'registered_temp_rolls_used': registered_temp_rolls_used
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

def sort_folder_data(data_list, sort_field, sort_direction, data_type):
    """Sort folder/project data by specified field and direction"""
    if not data_list:
        return data_list
    
    reverse_sort = sort_direction == 'desc'
    print(f"DEBUG sort_folder_data: data_type={data_type}, sort_field={sort_field}, direction={sort_direction}, count={len(data_list)}")
    
    try:
        if data_type == 'unanalyzed':
            # Sorting for unanalyzed folders
            if sort_field == 'name':
                return sorted(data_list, key=lambda x: x.get('folder_name', '').lower(), reverse=reverse_sort)
            elif sort_field == 'size':
                return sorted(data_list, key=lambda x: x.get('total_size', 0), reverse=reverse_sort)
            elif sort_field == 'files':
                return sorted(data_list, key=lambda x: x.get('file_count', 0), reverse=reverse_sort)
            elif sort_field == 'pdfs':
                return sorted(data_list, key=lambda x: x.get('pdf_count', 0), reverse=reverse_sort)
            elif sort_field == 'documents' or sort_field == 'pages':
                # For unanalyzed, sort by file count as fallback
                return sorted(data_list, key=lambda x: x.get('file_count', 0), reverse=reverse_sort)
            elif sort_field == 'date':
                # No date field for unanalyzed, fallback to name
                return sorted(data_list, key=lambda x: x.get('folder_name', '').lower(), reverse=reverse_sort)
                
        elif data_type == 'analyzed':
            # Sorting for analyzed folders
            if sort_field == 'name':
                return sorted(data_list, key=lambda x: x.get('folder_name', '').lower(), reverse=reverse_sort)
            elif sort_field == 'size':
                return sorted(data_list, key=lambda x: x.get('total_size', 0), reverse=reverse_sort)
            elif sort_field == 'documents':
                return sorted(data_list, key=lambda x: x.get('total_documents', 0), reverse=reverse_sort)
            elif sort_field == 'pages':
                return sorted(data_list, key=lambda x: x.get('total_pages', 0), reverse=reverse_sort)
            elif sort_field == 'files':
                return sorted(data_list, key=lambda x: x.get('file_count', 0), reverse=reverse_sort)
            elif sort_field == 'rolls':
                return sorted(data_list, key=lambda x: x.get('total_estimated_rolls', 0), reverse=reverse_sort)
            elif sort_field == 'utilization':
                return sorted(data_list, key=lambda x: x.get('overall_utilization', 0), reverse=reverse_sort)
            elif sort_field == 'oversized':
                return sorted(data_list, key=lambda x: x.get('oversized_count', 0), reverse=reverse_sort)
            elif sort_field == 'date':
                return sorted(data_list, key=lambda x: x.get('analyzed_at') or '', reverse=reverse_sort)
            elif sort_field == 'temp_created':
                return sorted(data_list, key=lambda x: x.get('estimated_temp_rolls_created', 0), reverse=reverse_sort)
            elif sort_field == 'temp_used':
                return sorted(data_list, key=lambda x: x.get('estimated_temp_rolls_used', 0), reverse=reverse_sort)
            elif sort_field == 'temp_strategy':
                return sorted(data_list, key=lambda x: x.get('temp_roll_strategy', 'none'), reverse=reverse_sort)
                
        elif data_type == 'registered':
            # Sorting for registered projects (note: many don't have size data)
            if sort_field == 'name':
                return sorted(data_list, key=lambda x: x['project'].archive_id.lower(), reverse=reverse_sort)
            elif sort_field == 'size':
                # Handle missing size data gracefully - use 0 as fallback
                return sorted(data_list, key=lambda x: x['data'].get('total_size', 0), reverse=reverse_sort)
            elif sort_field == 'documents':
                return sorted(data_list, key=lambda x: x['data'].get('total_documents', 0), reverse=reverse_sort)
            elif sort_field == 'pages':
                return sorted(data_list, key=lambda x: x['data'].get('total_pages', 0), reverse=reverse_sort)
            elif sort_field == 'rolls':
                return sorted(data_list, key=lambda x: x['data'].get('total_rolls', 0), reverse=reverse_sort)
            elif sort_field == 'location':
                return sorted(data_list, key=lambda x: (x['project'].location or '').lower(), reverse=reverse_sort)
            elif sort_field == 'status':
                # Sort by completion status
                def get_status_priority(item):
                    project = item['project']
                    if project.processing_complete:
                        return 4
                    elif project.film_allocation_complete:
                        return 3
                    elif item['data'].get('total_documents', 0) > 0:
                        return 2
                    else:
                        return 1
                return sorted(data_list, key=get_status_priority, reverse=reverse_sort)
            elif sort_field == 'date':
                return sorted(data_list, key=lambda x: x['project'].updated_at, reverse=reverse_sort)
            elif sort_field == 'temp_created':
                return sorted(data_list, key=lambda x: x['data'].get('temp_rolls_created', 0), reverse=reverse_sort)
            elif sort_field == 'temp_used':
                return sorted(data_list, key=lambda x: x['data'].get('temp_rolls_used', 0), reverse=reverse_sort)
            elif sort_field == 'temp_strategy':
                return sorted(data_list, key=lambda x: x['data'].get('temp_roll_strategy', 'none'), reverse=reverse_sort)
    
    except Exception as e:
        logger.error(f"Error sorting data: {e}")
        # Return original data if sorting fails
        return data_list
    
    # Default fallback - sort by name
    try:
        if data_type == 'registered':
            return sorted(data_list, key=lambda x: x['project'].archive_id.lower(), reverse=reverse_sort)
        else:
            return sorted(data_list, key=lambda x: x.get('folder_name', '').lower(), reverse=reverse_sort)
    except:
        return data_list 