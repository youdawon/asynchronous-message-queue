import asyncio
import websockets
import signal

STOP = asyncio.Event()

async def websocket_client():
    try:
        async with websockets.connect("ws://localhost:8003/ws") as websocket:
            print("WebSocket connected. Listening for messages...")
            while not STOP.is_set():
                try:
                    message = await websocket.recv()
                    print(f"Message received: {message}")
                except asyncio.CancelledError:
                    print("WebSocket client cancelled.")
                    break
    except Exception as e:
        print(f"WebSocket client error: {e}")
    finally:
        print("Closing WebSocket client.")

def shutdown():
    print("Shutdown signal received.")
    STOP.set()

if __name__ == "__main__":
    # Graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, lambda s, f: shutdown())

    try:
        asyncio.run(websocket_client())
    except KeyboardInterrupt:
        print("WebSocket client stopped manually.")

