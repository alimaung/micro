from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from ..services.sma_service import sma_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def start_filming(request):
    """
    Start a new filming process.
    
    Expected JSON payload:
    {
        "project_data": {
            "project_name": "Financial Records 2023",
            "folder_path": "/path/to/project",
            "total_documents": 423,
            "film_number": "F-16-0001"
        },
        "film_type": "16",  // "16" or "35"
        "recovery": false,
        "user_id": "user123"
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        project_data = data.get('project_data', {})
        if not project_data.get('folder_path'):
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: project_data.folder_path'
            }, status=400)
        
        film_type = data.get('film_type', '16')
        recovery = data.get('recovery', False)
        user_id = data.get('user_id')
        
        # Start the filming process
        result = sma_service.start_filming_process(
            project_data=project_data,
            film_type=film_type,
            recovery=recovery,
            user_id=user_id
        )
        
        if result['success']:
            return JsonResponse(result, status=201)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in start_filming: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def control_filming(request):
    """
    Control an active filming process (pause, resume, cancel).
    
    Expected JSON payload:
    {
        "session_id": "uuid-string",
        "action": "pause",  // "pause", "resume", "cancel"
        "user_id": "user123"
    }
    """
    try:
        data = json.loads(request.body)
        
        session_id = data.get('session_id')
        action = data.get('action')
        user_id = data.get('user_id')
        
        # Validate required fields
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: session_id'
            }, status=400)
        
        if action not in ['pause', 'resume', 'cancel']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action. Must be one of: pause, resume, cancel'
            }, status=400)
        
        # Control the filming process
        result = sma_service.control_filming_process(
            session_id=session_id,
            action=action,
            user_id=user_id
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in control_filming: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def filming_status(request, session_id):
    """
    Get the current status of a filming session.
    
    URL: /api/sma/status/{session_id}/
    """
    try:
        result = sma_service.get_session_status(session_id)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=404)
            
    except Exception as e:
        logger.error(f"Error in filming_status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def filming_logs(request, session_id):
    """
    Get logs for a filming session.
    
    URL: /api/sma/logs/{session_id}/?limit=100
    """
    try:
        limit = int(request.GET.get('limit', 100))
        
        result = sma_service.get_session_logs(session_id, limit=limit)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=404)
            
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid limit parameter'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in filming_logs: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def filming_progress(request, session_id):
    """
    Get progress data for a filming session.
    
    URL: /api/sma/progress/{session_id}/
    """
    try:
        result = sma_service.get_session_status(session_id)
        
        if result['success']:
            # Extract only progress-related data
            progress_data = {
                'success': True,
                'session_id': session_id,
                'progress_percent': result.get('progress_percent', 0),
                'processed_documents': result.get('processed_documents', 0),
                'total_documents': result.get('total_documents', 0),
                'eta': result.get('eta'),
                'processing_rate': result.get('processing_rate', 0),
                'current_step': result.get('current_step'),
                'status': result.get('status')
            }
            return JsonResponse(progress_data)
        else:
            return JsonResponse(result, status=404)
            
    except Exception as e:
        logger.error(f"Error in filming_progress: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def active_sessions(request):
    """
    Get all active filming sessions for the current user.
    
    URL: /api/sma/active-sessions/?user_id=user123
    """
    try:
        user_id = request.GET.get('user_id')
        
        result = sma_service.get_active_sessions(user_id=user_id)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in active_sessions: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def machine_status(request):
    """
    Get SMA machine status information.
    
    URL: /api/sma/machine-status/
    """
    try:
        # This would integrate with actual machine status checking
        # For now, return mock data
        machine_data = {
            'success': True,
            'machine_status': {
                'connected': True,
                'temperature': 28.4,
                'processing_speed': 3.2,
                'film_remaining': 65,
                'buffer_status': 32,
                'last_communication': '2024-01-15T10:30:00Z',
                'uptime': '2 days, 14 hours',
                'error_count': 0
            }
        }
        
        return JsonResponse(machine_data)
        
    except Exception as e:
        logger.error(f"Error in machine_status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def test_sma_connection(request):
    """
    Test connection to SMA system.
    
    Expected JSON payload:
    {
        "test_type": "basic"  // "basic", "full"
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        test_type = data.get('test_type', 'basic')
        
        # This would implement actual SMA connection testing
        # For now, return mock success
        result = {
            'success': True,
            'test_type': test_type,
            'connection_status': 'connected',
            'response_time_ms': 45,
            'version': 'SMA 51.2.1',
            'capabilities': ['filming', 'recovery', 'status_monitoring']
        }
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in test_sma_connection: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
