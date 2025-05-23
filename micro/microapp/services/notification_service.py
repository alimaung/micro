import json
import uuid
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Reusable notification service for handling Firebase, WebSocket, and in-app notifications.
    Can be used across different pages and routes.
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.firebase_available = self._check_firebase_availability()
    
    def _check_firebase_availability(self):
        """Check if Firebase is available and configured."""
        try:
            # Try to import Firebase if it exists
            import firebase_admin
            from firebase_admin import credentials, messaging
            return True
        except ImportError:
            logger.warning("Firebase not available - notifications will be limited to websockets and in-app")
            return False
    
    def send_notification(self, user_id, title, message, notification_type='general', data=None, channels=None):
        """
        Send a notification through multiple channels.
        
        Args:
            user_id (str): User identifier
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type of notification (general, sma_started, etc.)
            data (dict): Additional data to include
            channels (list): Specific channels to send to ['websocket', 'firebase', 'in_app']
        """
        if channels is None:
            channels = ['websocket', 'in_app']  # Default channels
        
        notification_id = str(uuid.uuid4())
        notification_data = {
            'id': notification_id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'data': data or {},
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        results = {}
        
        # Send through WebSocket if requested
        if 'websocket' in channels:
            results['websocket'] = self._send_websocket_notification(user_id, notification_data)
        
        # Send through Firebase if requested and available
        if 'firebase' in channels and self.firebase_available:
            results['firebase'] = self._send_firebase_notification_internal(title, message, notification_id)
        
        # Store in-app notification if requested
        if 'in_app' in channels:
            results['in_app'] = self._store_in_app_notification(notification_data)
        
        logger.info(f"Sent notification {notification_id} to user {user_id} via channels: {channels}")
        return {
            'success': True,
            'notification_id': notification_id,
            'channels': results
        }
    
    def send_websocket_notification(self, user_id, data, group_name=None):
        """
        Send a notification via WebSocket to a specific user or group.
        
        Args:
            user_id (str): User identifier
            data (dict): Data to send
            group_name (str): Optional group name (defaults to user-specific group)
        """
        try:
            if not group_name:
                group_name = f"user_{user_id}"
            
            if self.channel_layer:
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'notification_message',
                        'data': data
                    }
                )
                return {'success': True, 'group': group_name}
            else:
                logger.warning("Channel layer not available for WebSocket notifications")
                return {'success': False, 'error': 'Channel layer not available'}
                
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_firebase_notification(self, title, message, message_id, token=None):
        """
        Send a Firebase push notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            message_id (str): Message ID for grouping/replacing
            token (str): Optional specific device token
        """
        if not self.firebase_available:
            logger.warning("Firebase not available - skipping Firebase notification")
            return {'success': False, 'error': 'Firebase not available'}
        
        return self._send_firebase_notification_internal(title, message, message_id, token)
    
    def _send_firebase_notification_internal(self, title, message, message_id, token=None):
        """Internal Firebase notification sending."""
        try:
            import firebase_admin
            from firebase_admin import messaging
            
            # Use default token if none provided (you'd get this from user settings)
            if not token:
                token = getattr(settings, 'DEFAULT_FIREBASE_TOKEN', None)
                if not token:
                    return {'success': False, 'error': 'No Firebase token available'}
            
            # Construct the message
            firebase_message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                token=token,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        tag=message_id
                    )
                )
            )
            
            # Send the message
            response = messaging.send(firebase_message)
            logger.info(f"Firebase notification sent successfully: {response}")
            
            return {'success': True, 'response': response}
            
        except Exception as e:
            logger.error(f"Error sending Firebase notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_websocket_notification(self, user_id, notification_data):
        """Send notification via WebSocket."""
        return self.send_websocket_notification(user_id, {
            'type': 'notification',
            'notification': notification_data
        })
    
    def _store_in_app_notification(self, notification_data):
        """Store notification for in-app display."""
        try:
            user_id = notification_data['user_id']
            notification_id = notification_data['id']
            
            # Store individual notification
            cache_key = f"notification:{notification_id}"
            cache.set(cache_key, notification_data, timeout=604800)  # 7 days
            
            # Add to user's notification list
            user_notifications_key = f"user_notifications:{user_id}"
            user_notifications = cache.get(user_notifications_key, [])
            
            # Add new notification to the beginning
            user_notifications.insert(0, notification_id)
            
            # Keep only the last 100 notifications
            user_notifications = user_notifications[:100]
            
            # Store updated list
            cache.set(user_notifications_key, user_notifications, timeout=604800)  # 7 days
            
            return {'success': True, 'stored': True}
            
        except Exception as e:
            logger.error(f"Error storing in-app notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_user_notifications(self, user_id, limit=50, include_read=True):
        """
        Get notifications for a user.
        
        Args:
            user_id (str): User identifier
            limit (int): Maximum number of notifications to return
            include_read (bool): Whether to include read notifications
        """
        try:
            user_notifications_key = f"user_notifications:{user_id}"
            notification_ids = cache.get(user_notifications_key, [])
            
            notifications = []
            for notification_id in notification_ids[:limit]:
                cache_key = f"notification:{notification_id}"
                notification = cache.get(cache_key)
                
                if notification:
                    if include_read or not notification.get('read', False):
                        notifications.append(notification)
            
            return {
                'success': True,
                'notifications': notifications,
                'total': len(notification_ids)
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def mark_notification_read(self, notification_id, user_id=None):
        """
        Mark a notification as read.
        
        Args:
            notification_id (str): Notification identifier
            user_id (str): Optional user ID for validation
        """
        try:
            cache_key = f"notification:{notification_id}"
            notification = cache.get(cache_key)
            
            if not notification:
                return {'success': False, 'error': 'Notification not found'}
            
            # Validate user if provided
            if user_id and notification.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            # Mark as read
            notification['read'] = True
            notification['read_at'] = datetime.now().isoformat()
            
            # Update in cache
            cache.set(cache_key, notification, timeout=604800)  # 7 days
            
            return {'success': True, 'marked_read': True}
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def mark_all_read(self, user_id):
        """Mark all notifications as read for a user."""
        try:
            result = self.get_user_notifications(user_id, limit=100, include_read=True)
            if not result['success']:
                return result
            
            marked_count = 0
            for notification in result['notifications']:
                if not notification.get('read', False):
                    mark_result = self.mark_notification_read(notification['id'])
                    if mark_result['success']:
                        marked_count += 1
            
            return {
                'success': True,
                'marked_count': marked_count
            }
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications for a user."""
        try:
            result = self.get_user_notifications(user_id, include_read=False)
            if result['success']:
                return {
                    'success': True,
                    'unread_count': len(result['notifications'])
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_notification(self, notification_id, user_id=None):
        """
        Delete a notification.
        
        Args:
            notification_id (str): Notification identifier
            user_id (str): Optional user ID for validation
        """
        try:
            cache_key = f"notification:{notification_id}"
            notification = cache.get(cache_key)
            
            if not notification:
                return {'success': False, 'error': 'Notification not found'}
            
            # Validate user if provided
            if user_id and notification.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            # Remove from cache
            cache.delete(cache_key)
            
            # Remove from user's notification list
            user_notifications_key = f"user_notifications:{notification['user_id']}"
            user_notifications = cache.get(user_notifications_key, [])
            
            if notification_id in user_notifications:
                user_notifications.remove(notification_id)
                cache.set(user_notifications_key, user_notifications, timeout=604800)
            
            return {'success': True, 'deleted': True}
            
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_sma_progress_notification(self, user_id, session_id, progress_data):
        """
        Send SMA-specific progress notification via WebSocket.
        
        Args:
            user_id (str): User identifier
            session_id (str): SMA session identifier
            progress_data (dict): Progress information
        """
        return self.send_websocket_notification(
            user_id=user_id,
            data={
                'type': 'sma_progress',
                'session_id': session_id,
                'progress': progress_data
            },
            group_name=f"sma_session_{session_id}"
        )
    
    def send_sma_log_notification(self, user_id, session_id, log_entry):
        """
        Send SMA log entry via WebSocket.
        
        Args:
            user_id (str): User identifier
            session_id (str): SMA session identifier
            log_entry (dict): Log entry data
        """
        return self.send_websocket_notification(
            user_id=user_id,
            data={
                'type': 'sma_log',
                'session_id': session_id,
                'log': log_entry
            },
            group_name=f"sma_session_{session_id}"
        )
    
    def send_sma_status_notification(self, user_id, session_id, status_data):
        """
        Send SMA status change notification via WebSocket.
        
        Args:
            user_id (str): User identifier
            session_id (str): SMA session identifier
            status_data (dict): Status information
        """
        return self.send_websocket_notification(
            user_id=user_id,
            data={
                'type': 'sma_status',
                'session_id': session_id,
                'status': status_data
            },
            group_name=f"sma_session_{session_id}"
        )

# Singleton instance
notification_service = NotificationService()
