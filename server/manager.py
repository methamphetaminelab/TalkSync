from typing import Dict
from fastapi import WebSocket

class Manager:
    def __init__(self):
        try:
            self.active_clients: Dict[str, WebSocket] = {}
        except Exception as e:
            print(f"ERROR (manager.__init__): {e}")

    async def connect(self, websocket: WebSocket, userId: str):
        try:
            await websocket.accept()
            self.active_clients[userId] = websocket
            print(f"Client {userId} connected")
        except Exception as e:
            print(f"ERROR (manager.connect): {e}")

    async def disconnect(self, userId: str):
        try:
            if userId in self.active_clients:
                del self.active_clients[userId]
                print(f"Client {userId} disconnected")
        except Exception as e:
            print(f"ERROR (manager.disconnect): {e}")

    async def sendMessage(self, receiverId: str, message: str):
        try:
            client = self.active_clients.get(receiverId)
            if client:
                await client.send_text(message)   
        except Exception as e:
            print(f"ERROR (manager.sendMessage): {e}")

    async def broadcast(self, websocket, message: str):
        try:
            for client in self.active_clients.values():
                if client != websocket:
                    await client.send_text(message)
        except Exception as e:
            print(f"ERROR (manager.broadcast): {e}")