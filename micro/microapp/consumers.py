from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
import uuid

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