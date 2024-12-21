from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio
import websockets
import json

style = Style.from_dict({
    "prompt": "bold #00ff00",
    "input": "#ff6666",
    "message": "italic #00bfff",
    "error": "bold #ff0000",
    "command": "underline #ffff00",
})

commands = WordCompleter(
    ["connect", "disconnect", "send", "whisper", "chatmode", "help", "exit"],
    ignore_case=True
)

async def main():
    session = PromptSession()
    websocket = None
    print("\n╔═══════════════════╗\n║   TalkSync v2.1   ║\n╚═══════════════════╝\n")
    await print_help()

    with patch_stdout():
        while True:
            try:
                command = await session.prompt_async(
                    ">>> ",
                    completer=commands,
                    style=style,
                    complete_in_thread=True,
                )

                if command == "connect":
                    if websocket:
                        print("⚠️ You are already connected!")
                    else:
                        websocket = await connect(session)
                elif command == "disconnect":
                    await disconnect(websocket)
                    websocket = None
                elif command == "send":
                    if websocket:
                        text = await session.prompt_async("Enter message: ")
                        await send_global_message(websocket, text)
                    else:
                        print("⚠️ You must be connected to send messages.")
                elif command == "whisper":
                    if websocket:
                        receiver_id = await session.prompt_async("Enter receiver ID: ")
                        text = await session.prompt_async("Enter message: ")
                        await send_private_message(websocket, text, receiver_id)
                    else:
                        print("⚠️ You must be connected to send private messages.")
                elif command == "chatmode":
                    if websocket:
                        await chat_mode(websocket, session)
                    else:
                        print("⚠️ You must be connected to use chat mode.")
                elif command == "help":
                    await print_help()
                elif command == "exit":
                    print("\nGoodbye!")
                    break
                else:
                    print("⚠️ Unknown command. Type 'help' for a list of commands.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    if websocket:
        await websocket.close()

async def send_global_message(websocket, text: str):
    try:
        message = {
            "type": "globalMessage",
            "text": text
        }
        await websocket.send(json.dumps(message))
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

async def send_private_message(websocket, text: str, receiver_id: str):
    try:
        message = {
            "type": "privateMessage",
            "receiverId": receiver_id,
            "text": text
        }
        await websocket.send(json.dumps(message))
    except Exception as e:
        print(f"❌ Failed to send private message: {e}")

async def disconnect(websocket):
    try:
        if websocket:
            print("🔌 Disconnecting...")
            await websocket.close()
            print("✅ Disconnected.")
        else:
            print("⚠️ You are not connected to any server.")
    except Exception as e:
        print(f"❌ Failed to disconnect: {e}")

async def connect(session: PromptSession):
    try:
        address = await session.prompt_async("Enter server [ipAddress:port]: ")
        user_id = await session.prompt_async("Enter your [nickname]: ")
        uri = f"ws://{address}/ws/{user_id}"

        print("🔗 Connecting...")
        websocket = await websockets.connect(uri)
        asyncio.create_task(listen_for_message(websocket))
        print(f"✅ Connected to server as {user_id}.")
        return websocket
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

async def listen_for_message(websocket):
    try:
        while True:
            response = await websocket.recv()
            if response:
                print(f"💬 {response}")
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Connection closed.")
    except Exception as e:
        print(f"❌ Error while receiving messages: {e}")

async def chat_mode(websocket, session: PromptSession):
    try:
        print("-*- Chat mode enabled -*-\nType '::chatmode' to exit chat mode.")
        while True:
            text = await session.prompt_async("::: ")
            if text == "::chatmode":
                print("-*- Chat mode disabled -*-")
                break
            else:
                await send_global_message(websocket, text)
    except Exception as e:
        print(f"❌ Chat mode error: {e}")

async def print_help():
    try:
        print(
            "╔══════════════ HELP ═════════════╗\n"
            "║ connect    - Connect to server  ║\n"
            "║ disconnect - Disconnect         ║\n"
            "║ send       - Send global message║\n"
            "║ whisper    - Send private msg   ║\n"
            "║ chatmode   - Enter chat mode    ║\n"
            "║ help       - Show help          ║\n"
            "║ exit       - Exit program       ║\n"
            "╚═════════════════════════════════╝"
        )
    except Exception as e:
        print(f"❌ Failed to display help: {e}")

if __name__ == "__main__":
    asyncio.run(main())
