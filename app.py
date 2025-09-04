import asyncio

from websockets import ConnectionClosedOK
from websockets.asyncio.server import serve
import json


async def handler(ws_client):

    while True:
        try:
            message = json.loads(await ws_client.recv())
            print(f"Received: {message}")
            await ws_client.send(json.dumps({"ok": "ok"}))
        except ConnectionClosedOK as _:
            print("Connection closed")
            break

async def main():
    async with serve(handler, "localhost", 8005) as server:
        print(f"APP server running on ws://localhost:8000")
        await server.serve_forever()

if __name__ == "__main__":
    print("APP server running on ws://localhost:8000/ws")
    asyncio.run(main())

