from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from ..services.notification_service import notification_service

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def send_notification(request):
    """
    Send a notification through specified channels.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "title": "Notification Title",
        "message": "Notification message",
        "notification_type": "general",
        "data": {"key": "value"},
        "channels": ["websocket", "in_app"]
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        user_id = data.get('user_id')
        title = data.get('title')
        message = data.get('message')
        
        if not all([user_id, title, message]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: user_id, title, message'
            }, status=400)
        
        notification_type = data.get('notification_type', 'general')
        notification_data = data.get('data')
        channels = data.get('channels', ['websocket', 'in_app'])
        
        # Send the notification
        result = notification_service.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=notification_data,
            channels=channels
        )
        
        return JsonResponse(result, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in send_notification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def get_notifications(request):
    """
    Get notifications for a user.
    
    URL: /api/notifications/?user_id=user123&limit=50&include_read=true
    """
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: user_id'
            }, status=400)
        
        limit = int(request.GET.get('limit', 50))
        include_read = request.GET.get('include_read', 'true').lower() == 'true'
        
        result = notification_service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            include_read=include_read
        )
        
        return JsonResponse(result)
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid limit parameter'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in get_notifications: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    
    URL: /api/notifications/{notification_id}/read/
    
    Expected JSON payload:
    {
        "user_id": "user123"  // Optional for validation
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        user_id = data.get('user_id')
        
        result = notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=user_id
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in mark_notification_read: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mark_all_read(request):
    """
    Mark all notifications as read for a user.
    
    Expected JSON payload:
    {
        "user_id": "user123"
    }
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: user_id'
            }, status=400)
        
        result = notification_service.mark_all_read(user_id=user_id)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in mark_all_read: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def get_unread_count(request):
    """
    Get count of unread notifications for a user.
    
    URL: /api/notifications/unread-count/?user_id=user123
    """
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: user_id'
            }, status=400)
        
        result = notification_service.get_unread_count(user_id=user_id)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in get_unread_count: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """
    Delete a notification.
    
    URL: /api/notifications/{notification_id}/delete/
    
    Expected JSON payload:
    {
        "user_id": "user123"  // Optional for validation
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        user_id = data.get('user_id')
        
        result = notification_service.delete_notification(
            notification_id=notification_id,
            user_id=user_id
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in delete_notification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_firebase_notification(request):
    """
    Send a Firebase push notification directly.
    
    Expected JSON payload:
    {
        "title": "Notification Title",
        "message": "Notification message",
        "message_id": "unique_id",
        "token": "firebase_device_token"  // Optional
    }
    """
    try:
        data = json.loads(request.body)
        
        title = data.get('title')
        message = data.get('message')
        message_id = data.get('message_id')
        token = data.get('token')
        
        if not all([title, message, message_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: title, message, message_id'
            }, status=400)
        
        result = notification_service.send_firebase_notification(
            title=title,
            message=message,
            message_id=message_id,
            token=token
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in send_firebase_notification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_websocket_notification(request):
    """
    Send a WebSocket notification directly.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "data": {"type": "custom", "payload": "data"},
        "group_name": "optional_group_name"
    }
    """
    try:
        data = json.loads(request.body)
        
        user_id = data.get('user_id')
        notification_data = data.get('data')
        group_name = data.get('group_name')
        
        if not all([user_id, notification_data]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: user_id, data'
            }, status=400)
        
        result = notification_service.send_websocket_notification(
            user_id=user_id,
            data=notification_data,
            group_name=group_name
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in send_websocket_notification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def notification_settings(request):
    """
    Get notification settings for a user.
    
    URL: /api/notifications/settings/?user_id=user123
    """
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: user_id'
            }, status=400)
        
        # This would typically load from user preferences in database
        # For now, return default settings
        settings_data = {
            'success': True,
            'user_id': user_id,
            'settings': {
                'firebase_enabled': True,
                'websocket_enabled': True,
                'in_app_enabled': True,
                'sma_notifications': {
                    'progress_updates': True,
                    'completion_alerts': True,
                    'error_notifications': True,
                    'prep_alerts': True
                },
                'notification_frequency': {
                    'progress_interval': '2%',  # Every 2%
                    'prep_mode': 'percentage'   # 'percentage' or 'time'
                }
            }
        }
        
        return JsonResponse(settings_data)
        
    except Exception as e:
        logger.error(f"Error in notification_settings: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_notification_settings(request):
    """
    Update notification settings for a user.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "settings": {
            "firebase_enabled": true,
            "websocket_enabled": true,
            "sma_notifications": {
                "progress_updates": true,
                "completion_alerts": true
            }
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        user_id = data.get('user_id')
        settings = data.get('settings')
        
        if not all([user_id, settings]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: user_id, settings'
            }, status=400)
        
        # This would typically save to user preferences in database
        # For now, just return success
        result = {
            'success': True,
            'user_id': user_id,
            'message': 'Notification settings updated successfully',
            'updated_settings': settings
        }
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in update_notification_settings: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
