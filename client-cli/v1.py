import asyncio
import websockets
import json
import sys

async def connect(user_id: str):
    uri = f"ws://localhost:8000/ws/{user_id}"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to server as {user_id}\n")
            
            asyncio.create_task(listen_for_messages(websocket))
            
            while True:
                command = await asyncio.to_thread(input, "\nEnter a command (private <user_id> <message>, global <message>, exit): ")

                if command.startswith("private"):
                    _, receiver_id, text = command.split(maxsplit=2)
                    await send_private_message(websocket, receiver_id, text)
                elif command.startswith("global"):
                    _, text = command.split(maxsplit=1)
                    await send_global_message(websocket, text)
                elif command == "exit":
                    print("Disconnecting...")
                    break
                else:
                    print("Invalid command. Use 'private <user_id> <message>', 'global <message>', or 'exit'.")
            
    except (websockets.exceptions.WebSocketException, ConnectionRefusedError) as e:
        print(f"Error: Could not connect to the server. Please try again later.\n{e}")
        sys.exit(1)

async def listen_for_messages(websocket):
    try:
        while True:
            response = await websocket.recv()
            print(f"\n{response}")
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed.")

async def send_private_message(websocket, receiver_id: str, text: str):
    message = {
        "type": "privateMessage",
        "receiverId": receiver_id,
        "text": text
    }
    await websocket.send(json.dumps(message))
    print(f"Sent private message to {receiver_id}: {text}")

async def send_global_message(websocket, text: str):
    message = {
        "type": "globalMessage",
        "text": text
    }
    await websocket.send(json.dumps(message))
    print(f"Sent global message: {text}")

if __name__ == "__main__":
    user_id = input("Enter your user ID: ")
    asyncio.run(connect(user_id))
