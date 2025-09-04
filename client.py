import asyncio
import random

import websockets
import json

from websockets import ConnectionClosedOK


async def client_ws():
    await asyncio.sleep(random.randint(0, 20))
    uri = "ws://localhost:8765/ws"
    # Connect to WebSocket server
    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        # Send some JSON messages
        messages = [
            {"content": "Hello server!", "id": 1},
            {"content": "How are you?", "id": 2},
            {"content": "This is a test message", "id": 3}
        ]

        try:
            while True:
                for msg in messages:
                    await websocket.send(json.dumps(msg))

                    # Receive JSON response
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    print(f"Received: {response_data}")
                    print("-" * 100)
                    await asyncio.sleep(1)

                drop = random.randint(1, 10)
                if drop > 5:
                    print("Dropping connection")
                    await websocket.close()
                await asyncio.sleep(1)
        except ConnectionClosedOK as e:
            ...
        finally:
            print("Disconnected from server")

async def run_clients():
    clients_ws = [client_ws() for _ in range(5000)]
    await asyncio.gather(*clients_ws)

if __name__ == "__main__":
    asyncio.run(run_clients())