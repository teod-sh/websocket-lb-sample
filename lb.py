import asyncio
import random

import websockets
from websockets import ConnectionClosedOK
from websockets.asyncio.server import serve

targets = [
    "ws://localhost:8000/ws", "ws://localhost:8001/ws", "ws://localhost:8002/ws",
    "ws://localhost:8003/ws", "ws://localhost:8004/ws", "ws://localhost:8005/ws"
]

class RoundRobin:
    def __init__(self):
        self.targets = targets
        self.targets_connection_count = {target: 0 for target in targets}
        self.index = 0
        self._lock = asyncio.Lock()

    async def move_index(self):
        async with self._lock:
            # mock short living requests passing through the same load balancer
            move_by = random.randint(1, 5)
            while move_by > 0:
                self.index = (self.index + 1) % len(self.targets)
                move_by -= 1

    async def get_target(self):
        await self.move_index()

        async with self._lock:
            target = self.targets[self.index]
            self.index = (self.index + 1) % len(self.targets)
            return target

    async def increment_connection(self, target):
        async with self._lock:
            self.targets_connection_count[target] += 1

    async def decrement_connection(self, target):
        async with self._lock:
            self.targets_connection_count[target] -= 1

    async def print_metrics(self):
        print(self.targets_connection_count)
        # ...

class LeastConnection(RoundRobin):

    async def get_target(self):
        await self.move_index()

        async with self._lock:
            # instead of just move around the available the servers we consider who has fewer active connections
            target = min(self.targets_connection_count, key=self.targets_connection_count.get)
            return target

# LB = RoundRobin()
LB = LeastConnection()

async def propagate(from_ws, to_ws):
    while True:
        try:
            await to_ws.send(await from_ws.recv())
        except ConnectionClosedOK as _:
            # print("Connection closed")
            await to_ws.close()
            await from_ws.close()
            break


async def connect(ws_client):
    target = await LB.get_target()
    await LB.increment_connection(target)

    try:
        async with websockets.connect(target) as ws_server:
                # print(f"Connected to {target}")
                await asyncio.gather(
                    propagate(ws_client, ws_server),
                    propagate(ws_server, ws_client),
                    return_exceptions=True
                )
                # print(f"Disconnected from {target}")
    finally:
        await LB.decrement_connection(target)

async def print_metrics():
    while True:
        await LB.print_metrics()
        await asyncio.sleep(1)

async def main():
    asyncio.create_task(print_metrics())
    async with serve(connect, "localhost", 8765) as server:
        print(f"LB server running on ws://localhost:8765")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())