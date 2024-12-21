from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio
import websockets
import json

style = Style.from_dict({
    "prompt": "bold #00ff00",  # Применение яркого зеленого для подсказки
    "input": "#ff6666",        # Красный цвет для ввода
    "message": "#00bfff",      # Голубой для сообщений
    "error": "bold #ff0000",   # Ярко-красный для ошибок
    "command": "underline #ffff00",  # Подчеркнутый желтый для команд
})

commands = WordCompleter(
    ["connect", "disconnect", "send", "whisper", "chatmode", "help", "exit"],
    ignore_case=True
)

async def main():
    session = PromptSession()
    websocket = None
    print("\n-*- TalkSync v2 -*-\n")
    await printHelp()

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
                    websocket = await connect(session)
                elif command == "disconnect":
                    await disconnect(websocket)
                elif command == "send":
                    text = await session.prompt_async("Enter message: ")
                    await sendGlobalMessage(websocket, text)
                elif command == "whisper":
                    receiver_id = await session.prompt_async("Enter receiver ID: ")
                    text = await session.prompt_async("Enter message: ")
                    await sendPrivateMessage(websocket, text, receiver_id)
                elif command == "chatmode":
                    await chatMode(websocket, session)
                elif command == "help":
                    await printHelp()
                elif command == "exit":
                    print("\nExiting...")
                    break
                else:
                    print("Unknown command. Type 'help' for a list of commands.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

    if websocket:
        await websocket.close()

async def sendGlobalMessage(websocket, text: str):
    try:
        message = {
            "type": "globalMessage",
            "text": text
        }
        await websocket.send(json.dumps(message))
    except Exception as e:
        print(e)

async def sendPrivateMessage(websocket, text: str, receiverId: str):
    try:
        message = {
            "type": "privateMessage",
            "receiverId": receiverId,
            "text": text
        }
        await websocket.send(json.dumps(message))
    except Exception as e:
        print(e)

async def disconnect(websocket):
    try:
        if websocket:
            print("Disconnecting...")
            await websocket.close()
        else:
            print("You are not connected to the server.")
    except Exception as e:
        print(e)

async def connect(session: PromptSession):
    try:
        address = await session.prompt_async("Enter server [ipAddress:port]: ")
        userId = await session.prompt_async("Enter your [nickname]: ")
        uri = f"ws://{address}/ws/{userId}"

        websocket = await websockets.connect(uri)
        asyncio.create_task(listenForMessage(websocket))
        print(f"-*- Connected to server as {userId} -*-")
        return websocket
    except Exception as e:
        print(e)

async def listenForMessage(websocket):
    try:
        while True:
            response = await websocket.recv()
            if response:
                print(f"{response}")
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed.")
    except Exception as e:
        print(e)

async def chatMode(websocket, session: PromptSession):
    try:
        print("-*- Chat mode enabled -*-\n-*- (::chatmode to disable) -*-")
        while True:
            text = await session.prompt_async("::: ")
            if text == "::chatmode":
                print("-*- Chat mode disabled -*-")
                break
            else:
                await sendGlobalMessage(websocket, text)
    except Exception as e:
        print(e)

async def printHelp():
    try:
        print(
            "   connect - Connect to the server\n"
            "   disconnect - Disconnect from the server\n"
            "   send - Send a global message\n"
            "   chatmode - Enable chat mode\n"
            "   whisper - Send a private message\n"
            "   help - Show this help message\n"
            "   exit - Exit the client\n"
        )
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
