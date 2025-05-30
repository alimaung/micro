from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
import uuid
import logging
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .services.sma_service import SMAService
from .models import FilmingSession

logger = logging.getLogger(__name__)

class RelayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Create message queues
        self.response_queues = {}
        
        # Open persistent ESP32 connection
        self.esp32_ws = await websockets.connect('ws://192.168.1.101:81')
        self.esp32_connected = True
        
        # Set up a listening task to receive unsolicited messages from ESP32
        self.relay_listener_task = asyncio.create_task(self.listen_for_relay_messages())

    async def disconnect(self, close_code):
        # Cancel the listener task if it exists
        if hasattr(self, 'relay_listener_task'):
            self.relay_listener_task.cancel()
            
        # Close persistent ESP32 connection if open
        if hasattr(self, 'esp32_ws') and self.esp32_connected:
            await self.esp32_ws.close()
            self.esp32_connected = False

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # Handle disconnect
            if data.get('action') == 'disconnect':
                if hasattr(self, 'esp32_ws') and self.esp32_connected:
                    await self.esp32_ws.close()
                    self.esp32_connected = False
                await self.close()
                return

            # Handle light/dark mode
            if data.get('action') in ['dark', 'light']:
                requested_mode = data['action']
                # Define relay actions for each mode
                relay_commands = [
                    {"action": "pulse", "relay": 1},
                ]
                if requested_mode == 'dark':
                    relay_commands += [
                        {"action": "set", "relay": 2, "state": True},
                        {"action": "set", "relay": 3, "state": True},
                        {"action": "set", "relay": 4, "state": True},
                        {"action": "set", "relay": 5, "state": False}, # Turn OFF room light in dark mode
                    ]
                else:  # light
                    relay_commands += [
                        {"action": "set", "relay": 2, "state": False},
                        {"action": "set", "relay": 3, "state": False},
                        {"action": "set", "relay": 4, "state": False},
                        {"action": "set", "relay": 5, "state": True}, # Turn ON room light in light mode
                    ]

                # Send commands to ESP32
                if hasattr(self, 'esp32_ws') and self.esp32_connected:
                    try:
                        for cmd in relay_commands:
                            # Use our safe send/receive method that doesn't conflict with the listener
                            await self.send_and_receive(cmd)
                            
                        await self.send(json.dumps({'status': 'success', 'mode': requested_mode}))
                    except Exception as e:
                        print(f"Error in mode change: {str(e)}")
                        await self.send(json.dumps({'status': 'error', 'message': str(e)}))
                else:
                    await self.send(json.dumps({'status': 'error', 'message': 'ESP32 connection not available'}))
                return

            # Forward to ESP32 using persistent connection
            if hasattr(self, 'esp32_ws') and self.esp32_connected:
                try:
                    # Use our thread-safe method to send and receive
                    response = await self.send_and_receive(data)
                    await self.send(response)
                except Exception as e:
                    print(f"Error in request handling: {str(e)}")
                    await self.send(json.dumps({'status': 'error', 'message': str(e)}))
            else:
                await self.send(json.dumps({'status': 'error', 'message': 'ESP32 connection not available'}))
        except Exception as e:
            print(f"General error in receive: {str(e)}")
            await self.send(json.dumps({'status': 'error', 'message': str(e)}))
    
    async def send_and_receive(self, data):
        """Thread-safe method to send a command and get a response"""
        # Generate a unique message ID
        msg_id = str(uuid.uuid4())
        
        # Create a future for this request
        future = asyncio.Future()
        self.response_queues[msg_id] = future
        
        try:
            # Add message ID to outgoing request
            data_with_id = data.copy() if isinstance(data, dict) else {"action": "unknown"}
            data_with_id["msg_id"] = msg_id
            
            # Send the command
            await self.esp32_ws.send(json.dumps(data_with_id))
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=5.0)
            return response
        except asyncio.TimeoutError:
            # Handle timeout
            return json.dumps({'status': 'error', 'message': 'Timeout waiting for ESP32 response'})
        finally:
            # Clean up
            if msg_id in self.response_queues:
                del self.response_queues[msg_id]
    
    async def listen_for_relay_messages(self):
        """Background task that listens for messages from the ESP32 WebSocket connection"""
        try:
            while True:
                if hasattr(self, 'esp32_ws') and self.esp32_connected:
                    try:
                        # Wait for message from ESP32
                        message = await asyncio.wait_for(self.esp32_ws.recv(), timeout=0.5)
                        
                        # Process the received message
                        try:
                            # Try to parse it as JSON
                            msg_data = json.loads(message)
                            msg_type = msg_data.get('type', 'unknown')
                            
                            # Check if this message has a response ID
                            msg_id = msg_data.get('msg_id')
                            if msg_id and msg_id in self.response_queues:
                                # This is a response to a specific request
                                future = self.response_queues[msg_id]
                                if not future.done():
                                    future.set_result(message)
                                    print(f"Set result for request {msg_id}")
                                    continue
                            
                            # If no msg_id match, try the old way for backward compatibility
                            elif len(self.response_queues) > 0:
                                # Use the first waiting request (FIFO)
                                first_key = next(iter(self.response_queues))
                                future = self.response_queues[first_key]
                                if not future.done():
                                    future.set_result(message)
                                    print(f"Set result for first request {first_key}")
                                    continue
                            
                            # If we get here, this is an unsolicited message (like a button press)
                            # Forward to client
                            await self.send(message)
                            print(f"Forwarded unsolicited message of type '{msg_type}' to client")
                            
                        except json.JSONDecodeError:
                            # Non-JSON message
                            print("Received non-JSON message from ESP32")
                            await self.send(message)
                            
                    except asyncio.TimeoutError:
                        # No message received within timeout, just continue
                        pass
                    except websockets.exceptions.ConnectionClosed:
                        # Connection to ESP32 was closed
                        self.esp32_connected = False
                        print("ESP32 connection closed")
                        # Try to reconnect
                        try:
                            self.esp32_ws = await websockets.connect('ws://192.168.1.101:81')
                            self.esp32_connected = True
                            print("Reconnected to ESP32")
                        except:
                            # If reconnect fails, wait before trying again
                            await asyncio.sleep(5)
                else:
                    # No connection, wait a bit and try to establish one
                    await asyncio.sleep(5)
                    try:
                        self.esp32_ws = await websockets.connect('ws://192.168.1.101:81')
                        self.esp32_connected = True
                        print("Connected to ESP32")
                    except:
                        pass
                
                # Brief pause to prevent tight loop
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            print("Relay listener task cancelled")
            raise
        except Exception as e:
            print(f"Error in relay listener: {str(e)}")
            # Don't re-raise, try to keep the listener running

    # Add method to handle notification messages
    async def notification_message(self, event):
        """Handle notification messages sent from Django views"""
        await self.send(text_data=json.dumps(event['data']))


class SMAConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for SMA filming progress and control.
    Supports real-time progress updates, logs, and status changes.
    """
    
    async def connect(self):
        self.user_id = self.scope['query_string'].decode().split('user_id=')[-1] if 'user_id=' in self.scope['query_string'].decode() else 'anonymous'
        self.session_id = None
        
        # Add to user-specific group
        self.user_group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'user_id': self.user_id,
            'message': 'Connected to SMA WebSocket'
        }))

    async def disconnect(self, close_code):
        # Remove from user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        
        # Remove from session-specific group if joined
        if self.session_id:
            session_group_name = f"sma_session_{self.session_id}"
            await self.channel_layer.group_discard(
                session_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'join_session':
                # Join a specific session group for progress updates
                session_id = data.get('session_id')
                if session_id:
                    # Leave previous session group if any
                    if self.session_id:
                        old_group_name = f"sma_session_{self.session_id}"
                        await self.channel_layer.group_discard(
                            old_group_name,
                            self.channel_name
                        )
                    
                    # Join new session group
                    self.session_id = session_id
                    session_group_name = f"sma_session_{session_id}"
                    await self.channel_layer.group_add(
                        session_group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'session_joined',
                        'session_id': session_id,
                        'message': f'Joined session {session_id}'
                    }))
                    
            elif action == 'leave_session':
                # Leave current session group
                if self.session_id:
                    session_group_name = f"sma_session_{self.session_id}"
                    await self.channel_layer.group_discard(
                        session_group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'session_left',
                        'session_id': self.session_id,
                        'message': f'Left session {self.session_id}'
                    }))
                    
                    self.session_id = None
                    
            elif action == 'ping':
                # Simple ping/pong for connection testing
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown action: {action}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))

    # Handle different types of messages from Django
    async def notification_message(self, event):
        """Handle general notification messages"""
        await self.send(text_data=json.dumps(event['data']))

    async def sma_progress(self, event):
        """Handle SMA progress updates"""
        await self.send(text_data=json.dumps({
            'type': 'sma_progress',
            'session_id': event['session_id'],
            'progress': event['progress']
        }))

    async def sma_log(self, event):
        """Handle SMA log entries"""
        await self.send(text_data=json.dumps({
            'type': 'sma_log',
            'session_id': event['session_id'],
            'log': event['log']
        }))

    async def sma_status(self, event):
        """Handle SMA status changes"""
        await self.send(text_data=json.dumps({
            'type': 'sma_status',
            'session_id': event['session_id'],
            'status': event['status']
        }))

    async def sma_workflow_state(self, event):
        """Handle SMA workflow state changes"""
        await self.send(text_data=json.dumps({
            'type': 'sma_workflow_state',
            'session_id': event['session_id'],
            'old_state': event['old_state'],
            'new_state': event['new_state'],
            'timestamp': event.get('timestamp')
        }))

    async def sma_error(self, event):
        """Handle SMA error notifications"""
        await self.send(text_data=json.dumps({
            'type': 'sma_error',
            'session_id': event['session_id'],
            'error': event['error']
        }))

    async def sma_completed(self, event):
        """Handle SMA completion notifications"""
        await self.send(text_data=json.dumps({
            'type': 'sma_completed',
            'session_id': event['session_id'],
            'completion': event['completion']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    General-purpose notification consumer that can be used across different pages.
    Handles all types of notifications including SMA, system alerts, etc.
    """
    
    async def connect(self):
        self.user_id = self.scope['query_string'].decode().split('user_id=')[-1] if 'user_id=' in self.scope['query_string'].decode() else 'anonymous'
        
        # Add to user-specific group for general notifications
        self.user_group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'user_id': self.user_id,
            'message': 'Connected to notification WebSocket'
        }))

    async def disconnect(self, close_code):
        # Remove from user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                # Subscribe to specific notification types or groups
                subscription_type = data.get('type')
                subscription_id = data.get('id')
                
                if subscription_type and subscription_id:
                    group_name = f"{subscription_type}_{subscription_id}"
                    await self.channel_layer.group_add(
                        group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'subscription_type': subscription_type,
                        'subscription_id': subscription_id
                    }))
                    
            elif action == 'unsubscribe':
                # Unsubscribe from specific notification types or groups
                subscription_type = data.get('type')
                subscription_id = data.get('id')
                
                if subscription_type and subscription_id:
                    group_name = f"{subscription_type}_{subscription_id}"
                    await self.channel_layer.group_discard(
                        group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'unsubscribed',
                        'subscription_type': subscription_type,
                        'subscription_id': subscription_id
                    }))
                    
            elif action == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))

    # Handle all types of notification messages
    async def notification_message(self, event):
        """Handle any notification message"""
        await self.send(text_data=json.dumps(event['data']))

    async def system_alert(self, event):
        """Handle system alerts"""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'alert': event['alert']
        }))

    async def user_message(self, event):
        """Handle user-specific messages"""
        await self.send(text_data=json.dumps({
            'type': 'user_message',
            'message': event['message']
        }))


class SMAFilmingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for SMA filming real-time updates with enhanced functionality."""
    
    async def connect(self):
        """Handle WebSocket connection with authentication and session validation."""
        try:
            # Get session ID from URL
            self.session_id = self.scope['url_route']['kwargs']['session_id']
            self.group_name = f"sma_session_{self.session_id}"
        
            # Check authentication
            user = self.scope.get('user')
            if isinstance(user, AnonymousUser):
                logger.warning(f"Unauthenticated WebSocket connection attempt for session {self.session_id}")
                await self.close(code=4001)  # Custom close code for authentication failure
                return
        
            # Validate session access
            has_access = await self.check_session_access(user, self.session_id)
            if not has_access:
                logger.warning(f"User {user.username} denied access to session {self.session_id}")
                await self.close(code=4003)  # Custom close code for access denied
                return
        
            # Join session group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        
            # Send initial session status
            await self.send_initial_status()
        
            logger.info(f"User {user.username} connected to SMA session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error in WebSocket connect: {e}")
            await self.close(code=4000)  # Generic error
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection with cleanup."""
        try:
            # Leave session group
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            
                user = self.scope.get('user')
                if user and not isinstance(user, AnonymousUser):
                    logger.info(f"User {user.username} disconnected from SMA session {getattr(self, 'session_id', 'unknown')} (code: {close_code})")
                
        except Exception as e:
            logger.error(f"Error in WebSocket disconnect: {e}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages with command processing."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Handle different message types
            if message_type == 'ping':
                await self.send_pong()
            elif message_type == 'get_status':
                await self.send_current_status()
            elif message_type == 'subscribe_logs':
                await self.handle_log_subscription(data.get('level', 'info'))
            elif message_type == 'command':
                await self.handle_session_command(data)
            else:
                await self.send_error('Unknown message type')
        
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send_error('Internal error processing message')
    
    # SMA Event Handlers
    async def sma_progress(self, event):
        """Handle SMA progress updates with enhanced formatting."""
        try:
            progress_data = event['progress']
            
            # Add timestamp if not present
            if 'timestamp' not in progress_data:
                from datetime import datetime
                progress_data['timestamp'] = datetime.now().isoformat()
        
            await self.send(text_data=json.dumps({
                    'type': 'progress_update',
                    'session_id': event['session_id'],
                    'data': progress_data
                }))
        
        except Exception as e:
            logger.error(f"Error sending progress update: {e}")
    
    async def sma_workflow_state(self, event):
        """Handle SMA workflow state changes with transition information."""
        try:
            await self.send(text_data=json.dumps({
                'type': 'workflow_state_change',
                'session_id': event['session_id'],
                'old_state': event['old_state'],
                'new_state': event['new_state'],
                'timestamp': event.get('timestamp')
            }))
        
        except Exception as e:
            logger.error(f"Error sending workflow state change: {e}")
    
    async def sma_log(self, event):
        """Handle SMA log entries with filtering."""
        try:
            log_data = event['log']
            
            # Check if client is subscribed to this log level
            if hasattr(self, 'log_subscription_level'):
                log_levels = ['debug', 'info', 'warning', 'error', 'critical']
                if log_levels.index(log_data.get('level', 'info')) < log_levels.index(self.log_subscription_level):
                    return  # Skip this log entry
            
            await self.send(text_data=json.dumps({
                'type': 'log_entry',
                'session_id': event['session_id'],
                    'data': log_data
            }))
            
        except Exception as e:
            logger.error(f"Error sending log entry: {e}")
    
    async def sma_error(self, event):
        """Handle SMA error notifications with severity classification."""
        try:
            error_data = event['error']
            
            await self.send(text_data=json.dumps({
                'type': 'error',
                'session_id': event['session_id'],
                    'data': error_data,
                    'severity': error_data.get('severity', 'high'),
                    'timestamp': error_data.get('timestamp')
            }))
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    async def sma_completed(self, event):
        """Handle SMA completion notifications with summary information."""
        try:
            completion_data = event['completion']
            
            await self.send(text_data=json.dumps({
                'type': 'session_completed',
                'session_id': event['session_id'],
                    'data': completion_data,
                    'timestamp': completion_data.get('timestamp')
            }))

        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")
    
    async def sma_health_alert(self, event):
        """Handle SMA health alerts with actionable information."""
        try:
            health_data = event['health']
            
            await self.send(text_data=json.dumps({
                'type': 'health_alert',
                'session_id': event['session_id'],
                'data': health_data,
                'alert_level': health_data.get('alert_level', 'warning'),
                'timestamp': health_data.get('timestamp')
            }))
            
        except Exception as e:
            logger.error(f"Error sending health alert: {e}")
    
    # Helper Methods
    async def send_pong(self):
        """Send pong response to ping."""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': self.get_current_timestamp()
        }))
    
    async def send_current_status(self):
        """Send current session status to client."""
        try:
            from .services.sma_service import SMAService
            
            # Get status from service
            status_result = await database_sync_to_async(SMAService.get_session_status)(self.session_id)
            
            if status_result['success']:
                await self.send(text_data=json.dumps({
                        'type': 'status_update',
                        'session_id': self.session_id,
                        'data': status_result['status'],
                        'timestamp': self.get_current_timestamp()
                    }))
            else:
                await self.send_error(f"Failed to get status: {status_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending current status: {e}")
            await self.send_error('Failed to retrieve session status')
    
    async def send_initial_status(self):
        """Send initial session status when client connects."""
        await self.send_current_status()
    
    async def handle_log_subscription(self, level):
        """Handle log subscription level changes."""
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if level in valid_levels:
            self.log_subscription_level = level
            await self.send(text_data=json.dumps({
                'type': 'subscription_updated',
                'log_level': level,
                'timestamp': self.get_current_timestamp()
            }))
        else:
            await self.send_error(f'Invalid log level: {level}')
    
    async def handle_session_command(self, data):
        """Handle session control commands from WebSocket."""
        try:
            command = data.get('command')
            valid_commands = ['pause', 'resume', 'cancel', 'get_health']
            
            if command not in valid_commands:
                await self.send_error(f'Invalid command: {command}')
                return
            
            user = self.scope.get('user')
            
            # Check if user can control this session
            can_control = await self.check_session_control_access(user, self.session_id)
            if not can_control:
                await self.send_error('Access denied - insufficient permissions')
                return
            
            # Execute command
            from .services.sma_service import SMAService
            
            if command == 'pause':
                result = await database_sync_to_async(SMAService.pause_session)(self.session_id)
            elif command == 'resume':
                result = await database_sync_to_async(SMAService.resume_session)(self.session_id)
            elif command == 'cancel':
                result = await database_sync_to_async(SMAService.cancel_session)(self.session_id)
            elif command == 'get_health':
                result = await database_sync_to_async(SMAService.get_session_health)(self.session_id)
            
            # Send result back to client
            await self.send(text_data=json.dumps({
                'type': 'command_result',
                'command': command,
                'success': result.get('success', False),
                'data': result,
                'timestamp': self.get_current_timestamp()
            }))
        
        except Exception as e:
            logger.error(f"Error handling session command: {e}")
            await self.send_error('Failed to execute command')
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
        'message': message,
        'timestamp': self.get_current_timestamp()
        }))
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @database_sync_to_async
    def check_session_access(self, user, session_id):
        """Check if user has access to view this session."""
        try:
            from .models import FilmingSession
            
            # Staff users can access all sessions
            if user.is_staff:
                return True
            
            # Check if session exists and belongs to user
            session = FilmingSession.objects.filter(
                session_id=session_id,
                user=user
            ).first()
            
            return session is not None
        
        except Exception as e:
            logger.error(f"Error checking session access: {e}")
            return False
    
    @database_sync_to_async
    def check_session_control_access(self, user, session_id):
        """Check if user has permission to control this session."""
        try:
            from .models import FilmingSession
            
            # Staff users can control all sessions
            if user.is_staff:
                return True
            
            # Check if session exists and belongs to user
            session = FilmingSession.objects.filter(
                session_id=session_id,
                user=user,
                status__in=['running', 'paused']  # Only allow control of active sessions
            ).first()
            
            return session is not None
            
        except Exception as e:
            logger.error(f"Error checking session control access: {e}")
            return False


class GeneralNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for general system notifications."""
    
    async def connect(self):
        """Handle connection for general notifications."""
        try:
            # Check authentication
            user = self.scope.get('user')
            if isinstance(user, AnonymousUser):
                await self.close(code=4001)
                return
        
            # Join general notifications group
            self.group_name = "general_notifications"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        
            await self.accept()
            logger.info(f"User {user.username} connected to general notifications")
        
        except Exception as e:
            logger.error(f"Error in general notification connect: {e}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Handle disconnection from general notifications."""
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
        except Exception as e:
            logger.error(f"Error in general notification disconnect: {e}")
    
    async def system_notification(self, event):
        """Handle system-wide notifications."""
        try:
                await self.send(text_data=json.dumps({
                'type': 'system_notification',
                'data': event['data'],
                'timestamp': event.get('timestamp')
            }))
        except Exception as e:
            logger.error(f"Error sending system notification: {e}")
    
    async def session_alert(self, event):
        """Handle session-related alerts."""
        try:
            await self.send(text_data=json.dumps({
                    'type': 'session_alert',
                'session_id': event['session_id'],
                    'data': event['data'],
                    'timestamp': event.get('timestamp')
            }))
        except Exception as e:
            logger.error(f"Error sending session alert: {e}")