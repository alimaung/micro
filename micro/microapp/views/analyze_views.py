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
    """Main analyze dashboard showing all projects with analysis data"""
    analyze_service = AnalyzeService()
    
    # Get projects with analysis data
    projects_with_data = analyze_service.get_projects_with_analysis_data()
    
    # Apply search filter if provided
    search_query = request.GET.get('search', '')
    if search_query:
        filtered_projects = []
        for item in projects_with_data:
            project = item['project']
            if (search_query.lower() in project.archive_id.lower() or
                search_query.lower() in (project.location or '').lower() or
                search_query.lower() in (project.doc_type or '').lower()):
                filtered_projects.append(item)
        projects_with_data = filtered_projects
    
    # Apply status filter
    status_filter = request.GET.get('status', 'registered')
    if status_filter == 'all':
        # Show all projects
        all_projects = Project.objects.all().order_by('-updated_at')
        projects_with_data = []
        for project in all_projects:
            project_data = analyze_service.get_project_summary_data(project)
            projects_with_data.append({
                'project': project,
                'data': project_data or {}
            })
    
    # Pagination
    paginator = Paginator(projects_with_data, 12)  # 12 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate summary statistics
    total_projects = len(projects_with_data)
    total_documents = sum(item['data'].get('total_documents', 0) for item in projects_with_data)
    total_pages = sum(item['data'].get('total_pages', 0) for item in projects_with_data)
    projects_with_oversized = sum(1 for item in projects_with_data if item['data'].get('has_oversized', False))
    
    context = {
        'page_obj': page_obj,
        'projects_with_data': projects_with_data,
        'search_query': search_query,
        'status_filter': status_filter,
        'summary_stats': {
            'total_projects': total_projects,
            'total_documents': total_documents,
            'total_pages': total_pages,
            'projects_with_oversized': projects_with_oversized
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