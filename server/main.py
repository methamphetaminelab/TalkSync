from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import Manager
import json

app = FastAPI(
    title="TalkSync API",
    version="1.0.0"
)

manager = Manager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "privateMessage":
                receiverId = message["receiverId"]
                text = message["text"]
                await manager.sendMessage(receiverId, f"[PRIVATE] {user_id}: {text}")
            if message["type"] == "globalMessage":
                text = message["text"]
                await manager.broadcast(websocket, f"[GLOBAL] {user_id}: {text}")

    except WebSocketDisconnect:
        await manager.disconnect(user_id)
