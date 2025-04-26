from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio

class RelayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Open persistent ESP32 connection
        self.esp32_ws = await websockets.connect('ws://192.168.1.101:81')
        self.esp32_connected = True

    async def disconnect(self, close_code):
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
                    ]
                else:  # light
                    relay_commands += [
                        {"action": "set", "relay": 2, "state": False},
                        {"action": "set", "relay": 3, "state": False},
                        {"action": "set", "relay": 4, "state": False},
                    ]

                # Send commands to ESP32
                if hasattr(self, 'esp32_ws') and self.esp32_connected:
                    for cmd in relay_commands:
                        await self.esp32_ws.send(json.dumps(cmd))
                        
                        # Consume all pending messages until we get a timeout or specific response
                        while True:
                            try:
                                # Set a short timeout for additional messages
                                response = await asyncio.wait_for(self.esp32_ws.recv(), timeout=0.2)
                                # Optionally process or log the response
                                print(f"Received: {response}")
                            except asyncio.TimeoutError:
                                # No more immediate messages, continue to next command
                                break

                    await self.send(json.dumps({'status': 'success', 'mode': requested_mode}))
                else:
                    await self.send(json.dumps({'status': 'error', 'message': 'ESP32 connection not available'}))
                return

            # Forward to ESP32 using persistent connection
            if hasattr(self, 'esp32_ws') and self.esp32_connected:
                await self.esp32_ws.send(json.dumps(data))
                resp = await self.esp32_ws.recv()
                await self.send(resp)
            else:
                await self.send(json.dumps({'status': 'error', 'message': 'ESP32 connection not available'}))
        except Exception as e:
            await self.send(json.dumps({'status': 'error', 'message': str(e)}))