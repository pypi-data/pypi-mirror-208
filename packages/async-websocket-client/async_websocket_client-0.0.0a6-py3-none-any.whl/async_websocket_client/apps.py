from __future__ import annotations

import asyncio
import logging
from typing import Any, Coroutine

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError

from async_websocket_client.dispatchers import BaseDispatcher

# from sdk.client import BaseDispatcher


logger = logging.getLogger('async_websocket_client')


class AsyncWebSocketApp(object):
    url: str
    dispatcher: BaseDispatcher
    ws: WebSocketClientProtocol

    is_running: bool

    def __init__(self, url: str, dispatcher: BaseDispatcher):
        self.url = url
        self.dispatcher = dispatcher
        self.dispatcher.set_app(self)

        self.is_running = True

    async def connect(self):
        await self.dispatcher.before_connect()
        self.ws = await websockets.connect(self.url)
        await self.dispatcher.set_websocket(self.ws)
        await self.dispatcher.on_connect()

    async def disconnect(self):
        self.is_running = False

        await self.dispatcher.before_disconnect()
        await self.ws.close()
        await self.dispatcher.on_disconnect()

    async def send(self, message: str) -> Any:
        return asyncio.create_task(self.ws.send(message))

    async def ws_recv_loop(self):
        while self.is_running:
            message = await self.ws.recv()
            if message is None:
                continue

            await self.dispatcher.on_message(message)

    async def run(self):
        await self.connect()

        try:
            await self.ws_recv_loop()

        except asyncio.exceptions.CancelledError as ex:
            logger.error([type(ex), ex])

        except ConnectionClosedError as e:
            logger.error(f'Connection closed with error: {e}')

        self.is_running = False

        await self.disconnect()

    def asyncio_run(self):
        try:
            asyncio.run(self.run())

        except KeyboardInterrupt:
            logger.info('Correct exit')


class TasksMixin(AsyncWebSocketApp):

    tasks: list[Coroutine]
    _tasks: list[asyncio.Task]

    async def start_tasks(self):
        self._tasks = []
        for cor in self.tasks:
            logger.error(f'Start: {cor}')
            self._tasks.append(asyncio.create_task(cor))

    async def stop_tasks(self):
        for task in self._tasks:
            logger.error(f'Stop: {task}')
            await asyncio.wait_for(task, 10)

    async def connect(self):
        await super().connect()
        await self.start_tasks()

    async def disconnect(self):
        await self.stop_tasks()
        await super().disconnect()
